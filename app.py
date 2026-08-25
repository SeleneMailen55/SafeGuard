from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional
import google.generativeai as genai
import json
import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from PIL import Image
import bcrypt
import secrets
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(16))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///safeguard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "Debes iniciar sesión para acceder a este recurso"}), 401
    return redirect(url_for("login"))
# Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "TU_API_KEY_AQUI")
genai.configure(api_key=GEMINI_API_KEY)

# Crear directorios necesarios
os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)


# =========================
# MODELOS
# =========================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'niño', 'adulto'
    age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    analyses = db.relationship("Analysis", backref="user", lazy=True)
    activities = db.relationship("UserActivity", backref="user", lazy=True)
    contacts = db.relationship("TrustedContact", backref="user", lazy=True)


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # 'texto', 'imagen'
    content_hash = db.Column(db.String(255), nullable=True)
    is_grooming = db.Column(db.Boolean, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    signals_detected = db.Column(db.Text, nullable=True)  # JSON
    explanation = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)  # JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class TrustedContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    relationship = db.Column(db.String(50), nullable=False)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatSimulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    scenario_name = db.Column(db.String(100), nullable=False)
    messages = db.Column(db.Text, nullable=False)  # JSON
    user_responses = db.Column(db.Text, nullable=True)  # JSON
    safety_score = db.Column(db.Integer, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# FORMULARIOS
# =========================
class LoginForm(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Contraseña", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Correo electrónico", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField("Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    role = SelectField(
        "Rol",
        choices=[("niño", "Niño/Adolescente"), ("adulto", "Adulto/Padre/Tutor")],
        validators=[DataRequired()]
    )
    age = IntegerField("Edad", validators=[Optional(), NumberRange(min=6, max=99)])


class TrustedContactForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    email = StringField("Correo electrónico", validators=[Optional(), Email()])
    relationship = SelectField(
        "Relación",
        choices=[
            ("padre", "Padre"),
            ("madre", "Madre"),
            ("tutor", "Tutor/Guardián"),
            ("maestro", "Maestro/Profesor"),
            ("familia", "Familiar"),
            ("otro", "Otro")
        ],
        validators=[DataRequired()]
    )
    is_emergency = BooleanField("Contacto de emergencia")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =========================
# HELPERS
# =========================
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode("utf-8"), hashed_password.encode("utf-8"))


def analizar_con_gemini(texto, es_imagen=False, user_context=None):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        context_info = ""
        if user_context:
            context_info = f"""
            Contexto del usuario:
            - Edad: {user_context.get('age', 'No especificada')}
            - Rol: {user_context.get('role', 'No especificado')}
            - Historial de análisis: {user_context.get('previous_analyses', 0)} análisis previos
            """

        prompt = f"""
        Eres un experto en seguridad infantil y detección de grooming. Analiza el siguiente contenido y determina si contiene señales de grooming o comportamiento predatorio hacia menores.

        {context_info}

        Factores a considerar:
        - Solicitudes de información personal (dirección, escuela, horarios)
        - Intentos de establecer secretos o confidencialidad
        - Lenguaje sexualmente sugestivo o inapropiado
        - Intentos de aislar al menor de familia/amigos
        - Ofertas de regalos, dinero o favores
        - Solicitudes de fotos o videos, especialmente íntimos
        - Intentos de encuentros físicos o citas
        - Manipulación emocional o chantaje
        - Uso de lenguaje adulador excesivo
        - Comportamiento posesivo o controlador
        - Referencias a "amor" o relaciones románticas con menores
        - Solicitudes de guardar secretos de los padres

        Responde en formato JSON con la siguiente estructura:
        {{
            "es_grooming": true/false,
            "nivel_riesgo": "bajo/medio/alto",
            "porcentaje_riesgo": 0-100,
            "señales_detectadas": ["lista de señales encontradas"],
            "explicacion": "explicación detallada del análisis",
            "recomendaciones": ["lista de recomendaciones específicas"],
            "acciones_inmediatas": ["acciones a tomar de inmediato si es necesario"],
            "gravedad": "baja/moderada/alta/crítica"
        }}

        Contenido a analizar:
        """

        if es_imagen:
            response = model.generate_content([prompt, texto])
        else:
            response = model.generate_content(prompt + texto)

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        result = json.loads(response_text)

        if "porcentaje_riesgo" not in result:
            if result.get("nivel_riesgo") == "alto":
                result["porcentaje_riesgo"] = 85
            elif result.get("nivel_riesgo") == "medio":
                result["porcentaje_riesgo"] = 50
            else:
                result["porcentaje_riesgo"] = 15

        return result

    except Exception as e:
        return {
            "es_grooming": False,
            "nivel_riesgo": "error",
            "porcentaje_riesgo": 0,
            "señales_detectadas": [],
            "explicacion": f"Error en el análisis: {str(e)}",
            "recomendaciones": ["Intenta el análisis nuevamente"],
            "acciones_inmediatas": ["Verificar conexión a internet"],
            "gravedad": "baja"
        }


def calculate_quiz_score(quiz_type, answers):
    correct_answers_db = {
        "safety": {
            "q1": "nunca",
            "q2": "hablar_adulto",
            "q3": "no_responder",
            "q4": "todas",
            "q5": "inmediatamente"
        }
    }

    correct = 0
    quiz_answers = correct_answers_db.get(quiz_type, {})
    for question, correct_answer in quiz_answers.items():
        if answers.get(question) == correct_answer:
            correct += 1
    return correct


def get_score_message(score):
    if score >= 90:
        return "¡Excelente! Tienes muy buenos conocimientos sobre seguridad en línea."
    if score >= 70:
        return "¡Bien hecho! Tienes buenos conocimientos, pero puedes mejorar un poco más."
    if score >= 50:
        return "Regular. Es importante que repases la información de seguridad."
    return "Necesitas aprender más sobre seguridad en línea. ¡Sigue practicando!"


def create_tables():
    with app.app_context():
        db.create_all()


# =========================
# RUTAS PÚBLICAS
# =========================
@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "niño":
            return redirect(url_for("dashboard_nino"))
        return redirect(url_for("dashboard_adulto"))
    return render_template("index.html")


@app.route("/ninos")
def seccion_ninos():
    return render_template("ninos.html")


@app.route("/adultos")
def seccion_adultos():
    return render_template("adultos.html")

##
@app.route("/api/public/analyze", methods=["POST"])
def api_public_analyze():
    try:
        data = request.get_json() or {}
        texto = data.get("mensaje", "").strip()

        if not texto:
            return jsonify({"error": "No se proporcionó texto para analizar"}), 400

        resultado = analizar_con_gemini(texto, user_context=None)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": f"Error procesando solicitud: {str(e)}"}), 500


@app.route("/api/public/analyze-image", methods=["POST"])
def api_public_analyze_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No se proporcionó imagen"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No se seleccionó archivo"}), 400

        allowed_extensions = {"png", "jpg", "jpeg", "gif"}
        if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400

        file_bytes = file.read()
        image = Image.open(io.BytesIO(file_bytes))

        resultado = analizar_con_gemini(image, es_imagen=True, user_context=None)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": f"Error procesando imagen: {str(e)}"}), 500
##

@app.route("/inicio")
def inicio():
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password(user.password_hash, form.password.data):
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))

        flash("Usuario o contraseña incorrectos", "error")

    return render_template("auth/login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("El nombre de usuario ya está en uso", "error")
            return render_template("auth/register.html", form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash("El correo electrónico ya está registrado", "error")
            return render_template("auth/register.html", form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hash_password(form.password.data),
            role=form.role.data,
            age=form.age.data
        )

        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        flash("¡Registro exitoso! Bienvenido a SafeGuard", "success")
        return redirect(url_for("index"))

    return render_template("auth/register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión exitosamente", "info")
    return redirect(url_for("index"))


# =========================
# DASHBOARDS
# =========================
@app.route("/dashboard/nino")
@login_required
def dashboard_nino():
    if current_user.role != "niño":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))

    total_activities = UserActivity.query.filter_by(user_id=current_user.id).count()
    completed_activities = UserActivity.query.filter_by(user_id=current_user.id, completed=True).count()
    quiz_scores = UserActivity.query.filter_by(user_id=current_user.id, activity_type="quiz").all()

    avg_score = 0
    if quiz_scores:
        avg_score = sum(activity.score or 0 for activity in quiz_scores) / len(quiz_scores)

    trusted_contacts = TrustedContact.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "dashboard/nino.html",
        total_activities=total_activities,
        completed_activities=completed_activities,
        avg_score=round(avg_score),
        trusted_contacts=trusted_contacts
    )


@app.route("/dashboard/adulto")
@login_required
def dashboard_adulto():
    if current_user.role != "adulto":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))

    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    threats_detected = Analysis.query.filter_by(user_id=current_user.id, is_grooming=True).count()
    recent_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.timestamp.desc())
        .limit(5)
        .all()
    )

    detection_rate = (threats_detected / total_analyses * 100) if total_analyses > 0 else 0

    return render_template(
        "dashboard/adulto.html",
        total_analyses=total_analyses,
        threats_detected=threats_detected,
        detection_rate=round(detection_rate, 1),
        recent_analyses=recent_analyses
    )


# =========================
# SECCIÓN KIDS
# =========================
@app.route("/kids/quiz")
@login_required
def kids_quiz():
    if current_user.role != "niño":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))
    return render_template("kids/quiz.html")


@app.route("/kids/chat-sim")
@login_required
def kids_chat_simulation():
    if current_user.role != "niño":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))
    return render_template("kids/chat_simulation.html")


@app.route("/kids/contacts")
@login_required
def kids_contacts():
    if current_user.role != "niño":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))

    contacts = TrustedContact.query.filter_by(user_id=current_user.id).all()
    form = TrustedContactForm()
    return render_template("kids/contacts.html", contacts=contacts, form=form)


# =========================
# PÁGINAS ADULTO
# =========================
@app.route("/analyze")
@login_required
def analyze_page():
    if current_user.role != "adulto":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))
    return render_template("analyze.html")


@app.route("/voice-assistant")
@login_required
def voice_assistant_page():
    return render_template("voice_assistant.html")


@app.route("/chat-nlp")
@login_required
def chat_nlp_page():
    return render_template("chat_nlp.html")


@app.route("/reports")
@login_required
def reports_page():
    if current_user.role != "adulto":
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))

    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    threats_detected = Analysis.query.filter_by(user_id=current_user.id, is_grooming=True).count()

    today = datetime.utcnow().date()
    daily_analyses = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.timestamp >= datetime.combine(today, datetime.min.time())
    ).count()

    weekly_analyses = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()

    monthly_analyses = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.timestamp >= datetime.utcnow() - timedelta(days=30)
    ).count()

    return render_template(
        "reports.html",
        total_analyses=total_analyses,
        threats_detected=threats_detected,
        daily_analyses=daily_analyses,
        weekly_analyses=weekly_analyses,
        monthly_analyses=monthly_analyses
    )


# =========================
# API
# =========================
@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    if current_user.role != "adulto":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}
        texto = data.get("mensaje", "").strip()

        if not texto:
            return jsonify({"error": "No se proporcionó texto para analizar"}), 400

        user_context = {
            "age": current_user.age,
            "role": current_user.role,
            "previous_analyses": Analysis.query.filter_by(user_id=current_user.id).count()
        }

        resultado = analizar_con_gemini(texto, user_context=user_context)

        analysis = Analysis(
            user_id=current_user.id,
            content_type="texto",
            content_hash=hashlib.md5(texto.encode()).hexdigest(),
            is_grooming=resultado.get("es_grooming", False),
            risk_level=resultado.get("nivel_riesgo", "bajo"),
            signals_detected=json.dumps(resultado.get("señales_detectadas", []), ensure_ascii=False),
            explanation=resultado.get("explicacion", ""),
            recommendations=json.dumps(resultado.get("recomendaciones", []), ensure_ascii=False)
        )

        db.session.add(analysis)
        db.session.commit()

        return jsonify(resultado)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error procesando solicitud: {str(e)}"}), 500


@app.route("/api/analyze-image", methods=["POST"])
@login_required
def api_analyze_image():
    if current_user.role != "adulto":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        if "image" not in request.files:
            return jsonify({"error": "No se proporcionó imagen"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No se seleccionó archivo"}), 400

        allowed_extensions = {"png", "jpg", "jpeg", "gif"}
        if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400

        file_bytes = file.read()
        image = Image.open(io.BytesIO(file_bytes))

        user_context = {
            "age": current_user.age,
            "role": current_user.role,
            "previous_analyses": Analysis.query.filter_by(user_id=current_user.id).count()
        }

        resultado = analizar_con_gemini(image, es_imagen=True, user_context=user_context)

        analysis = Analysis(
            user_id=current_user.id,
            content_type="imagen",
            content_hash=hashlib.md5(file_bytes).hexdigest(),
            is_grooming=resultado.get("es_grooming", False),
            risk_level=resultado.get("nivel_riesgo", "bajo"),
            signals_detected=json.dumps(resultado.get("señales_detectadas", []), ensure_ascii=False),
            explanation=resultado.get("explicacion", ""),
            recommendations=json.dumps(resultado.get("recomendaciones", []), ensure_ascii=False)
        )

        db.session.add(analysis)
        db.session.commit()

        return jsonify(resultado)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error procesando imagen: {str(e)}"}), 500


@app.route("/api/quiz/submit", methods=["POST"])
@login_required
def api_quiz_submit():
    if current_user.role != "niño":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}
        answers = data.get("answers", {})
        quiz_type = data.get("quiz_type", "safety")

        correct_answers = calculate_quiz_score(quiz_type, answers)
        total_questions = len(answers)
        score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

        activity = UserActivity(
            user_id=current_user.id,
            activity_type="quiz",
            data=json.dumps(
                {
                    "quiz_type": quiz_type,
                    "answers": answers,
                    "correct_answers": correct_answers,
                    "total_questions": total_questions
                },
                ensure_ascii=False
            ),
            score=score,
            completed=True
        )

        db.session.add(activity)
        db.session.commit()

        return jsonify(
            {
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "message": get_score_message(score)
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error procesando quiz: {str(e)}"}), 500


@app.route("/api/contacts/add", methods=["POST"])
@login_required
def api_add_contact():
    if current_user.role != "niño":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}

        if not data.get("name", "").strip():
            return jsonify({"success": False, "errors": {"name": ["El nombre es requerido"]}}), 400

        if not data.get("phone", "").strip() and not data.get("email", "").strip():
            return jsonify(
                {"success": False, "errors": {"general": ["Debe proporcionar al menos teléfono o email"]}},
                400
            )

        contact = TrustedContact(
            user_id=current_user.id,
            name=data.get("name", "").strip(),
            phone=data.get("phone", "").strip() or None,
            email=data.get("email", "").strip() or None,
            relationship=data.get("relationship", "otro"),
            is_emergency=data.get("is_emergency") in [True, "true", "on", "1", 1]
        )

        db.session.add(contact)
        db.session.commit()

        return jsonify({"success": True, "message": "Contacto agregado exitosamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/voice-assistant", methods=["POST"])
@login_required
def voice_assistant():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "No se proporcionó mensaje"}), 400

        context_prompt = f"""
        Eres SARA (Sistema de Asistencia y Respuesta Automatizada), un asistente de voz especializado en seguridad infantil y prevención de grooming.

        Información del usuario:
        - Edad: {current_user.age if current_user.age else 'No especificada'}
        - Rol: {current_user.role}
        - Nombre: {current_user.username}

        Tu personalidad:
        - Amigable pero profesional
        - Comprensiva y empática
        - Educativa sin ser condescendiente
        - Siempre enfocada en la seguridad

        Responde de manera conversacional, como si estuvieras hablando en voz alta.
        Máximo 150 palabras.

        Si el usuario pregunta sobre situaciones peligrosas, ofrece ayuda inmediata y sugiere hablar con un adulto de confianza.

        Mensaje del usuario: {user_message}
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(context_prompt)

        return jsonify({
            "response": response.text,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Error en asistente de voz: {str(e)}"}), 500


@app.route("/api/chat-nlp", methods=["POST"])
@login_required
def chat_nlp():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()
        chat_history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "No se proporcionó mensaje"}), 400

        conversation_context = ""
        if chat_history:
            conversation_context = "\n".join(
                [f"Usuario: {msg.get('user', '')}\nBot: {msg.get('bot', '')}" for msg in chat_history[-5:]]
            )

        context_prompt = f"""
        Eres ChatGuard, un chatbot inteligente especializado en educación sobre seguridad digital y prevención de grooming.

        Información del usuario:
        - Edad: {current_user.age if current_user.age else 'No especificada'}
        - Rol: {current_user.role}

        Conversación previa:
        {conversation_context}

        Tu función:
        - Educar sobre seguridad online de manera interactiva
        - Detectar si el usuario necesita ayuda inmediata
        - Proporcionar información sobre grooming y ciberseguridad
        - Ser empático y comprensivo
        - Adaptar tu lenguaje a la edad del usuario

        Reglas importantes:
        - Si detectas que el usuario está en peligro inmediato, sugiere contactar autoridades o adultos
        - Mantén un tono amigable pero educativo
        - Proporciona ejemplos prácticos
        - Respuestas máximo 200 palabras

        Mensaje actual del usuario: {user_message}
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(context_prompt)

        activity = UserActivity(
            user_id=current_user.id,
            activity_type="chat_nlp",
            data=json.dumps(
                {
                    "user_message": user_message,
                    "bot_response": response.text,
                    "timestamp": datetime.utcnow().isoformat()
                },
                ensure_ascii=False
            ),
            completed=True
        )

        db.session.add(activity)
        db.session.commit()

        return jsonify({
            "response": response.text,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en chat NLP: {str(e)}"}), 500


@app.route("/api/chat-simulation/submit", methods=["POST"])
@login_required
def submit_chat_simulation():
    if current_user.role != "niño":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}
        responses = data.get("responses", [])
        score = data.get("score", 0)

        simulation = ChatSimulation(
            user_id=current_user.id,
            scenario_name="Simulador Avanzado",
            messages=json.dumps([], ensure_ascii=False),
            user_responses=json.dumps(responses, ensure_ascii=False),
            safety_score=score,
            completed=True
        )
        db.session.add(simulation)

        activity = UserActivity(
            user_id=current_user.id,
            activity_type="chat_simulation",
            data=json.dumps(
                {
                    "responses": responses,
                    "score": score,
                    "scenarios_completed": len(responses)
                },
                ensure_ascii=False
            ),
            score=score,
            completed=True
        )
        db.session.add(activity)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Simulación guardada exitosamente",
            "score": score
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error guardando simulación: {str(e)}"}), 500


@app.route("/api/generate-pdf", methods=["POST"])
@login_required
def generate_pdf_report():
    if current_user.role != "adulto":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}
        report_type = data.get("type", "full")

        if report_type == "daily":
            from_date = datetime.utcnow() - timedelta(days=1)
            analyses = Analysis.query.filter(
                Analysis.user_id == current_user.id,
                Analysis.timestamp >= from_date
            ).all()
            title = "Reporte Diario"
        elif report_type == "weekly":
            from_date = datetime.utcnow() - timedelta(days=7)
            analyses = Analysis.query.filter(
                Analysis.user_id == current_user.id,
                Analysis.timestamp >= from_date
            ).all()
            title = "Reporte Semanal"
        else:
            analyses = Analysis.query.filter_by(user_id=current_user.id).all()
            title = "Reporte Completo"

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph(f"SafeGuard - {title}", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Usuario: {current_user.username}", styles["Normal"]))
        story.append(Paragraph(f"Fecha: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        story.append(Spacer(1, 20))

        total_analyses = len(analyses)
        threats_detected = sum(1 for a in analyses if a.is_grooming)

        summary_data = [
            ["Métrica", "Valor"],
            ["Total de análisis", str(total_analyses)],
            ["Amenazas detectadas", str(threats_detected)],
            ["Contenido seguro", str(total_analyses - threats_detected)],
            ["Tasa de detección", f"{(threats_detected / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(Paragraph("Resumen Estadístico", styles["Heading2"]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        if analyses:
            story.append(Paragraph("Detalle de Análisis", styles["Heading2"]))
            for analysis in analyses[-10:]:
                story.append(Paragraph(f"Fecha: {analysis.timestamp.strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
                story.append(Paragraph(f"Tipo: {analysis.content_type.title()}", styles["Normal"]))
                story.append(Paragraph(f"Riesgo: {analysis.risk_level.title()}", styles["Normal"]))
                story.append(Paragraph(f"Amenaza: {'Sí' if analysis.is_grooming else 'No'}", styles["Normal"]))

                if analysis.explanation:
                    explanation = analysis.explanation
                    if len(explanation) > 200:
                        explanation = explanation[:200] + "..."
                    story.append(Paragraph(f"Explicación: {explanation}", styles["Normal"]))

                story.append(Spacer(1, 12))

        doc.build(story)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"safeguard_{report_type}_report.pdf"
        )

    except Exception as e:
        return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500


@app.route("/api/generate-advanced-pdf", methods=["POST"])
@login_required
def generate_advanced_pdf():
    if current_user.role != "adulto":
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        data = request.get_json() or {}
        report_config = {
            "type": data.get("type", "custom"),
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "include_statistics": data.get("include_statistics", True),
            "include_details": data.get("include_details", True),
            "include_recommendations": data.get("include_recommendations", True),
            "risk_levels": data.get("risk_levels", ["bajo", "medio", "alto"]),
            "content_types": data.get("content_types", ["texto", "imagen"])
        }

        query = Analysis.query.filter_by(user_id=current_user.id)

        if report_config["start_date"]:
            start_date = datetime.fromisoformat(report_config["start_date"])
            query = query.filter(Analysis.timestamp >= start_date)

        if report_config["end_date"]:
            end_date = datetime.fromisoformat(report_config["end_date"])
            query = query.filter(Analysis.timestamp <= end_date)

        if report_config["risk_levels"]:
            query = query.filter(Analysis.risk_level.in_(report_config["risk_levels"]))

        if report_config["content_types"]:
            query = query.filter(Analysis.content_type.in_(report_config["content_types"]))

        analyses = query.order_by(Analysis.timestamp.desc()).all()

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=1 * inch)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=28,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor("#2C3E50")
        )
        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor("#34495E")
        )

        story.append(Paragraph("SAFEGUARD", title_style))
        story.append(Paragraph("Reporte de Análisis de Seguridad Digital", subtitle_style))
        story.append(Spacer(1, 50))

        info_data = [
            ["Usuario:", current_user.username],
            ["Período:", f"Desde {report_config.get('start_date', 'inicio')} hasta {report_config.get('end_date', 'ahora')}"],
            ["Fecha de generación:", datetime.utcnow().strftime("%d/%m/%Y %H:%M")],
            ["Total de análisis:", str(len(analyses))],
            ["Versión:", "SafeGuard v2.0"]
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
            ("GRID", (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 30))

        if report_config["include_statistics"]:
            story.append(Paragraph("RESUMEN EJECUTIVO", subtitle_style))

            total_analyses = len(analyses)
            threats_detected = sum(1 for a in analyses if a.is_grooming)
            safe_content = total_analyses - threats_detected

            risk_stats = {level: sum(1 for a in analyses if a.risk_level == level) for level in ["bajo", "medio", "alto"]}
            content_stats = {ct: sum(1 for a in analyses if a.content_type == ct) for ct in ["texto", "imagen"]}

            summary_data = [
                ["MÉTRICA", "CANTIDAD", "PORCENTAJE"],
                ["Total de análisis realizados", str(total_analyses), "100%"],
                ["Amenazas detectadas", str(threats_detected), f"{(threats_detected / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["Contenido seguro", str(safe_content), f"{(safe_content / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["", "", ""],
                ["ANÁLISIS POR NIVEL DE RIESGO", "", ""],
                ["Riesgo bajo", str(risk_stats["bajo"]), f"{(risk_stats['bajo'] / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["Riesgo medio", str(risk_stats["medio"]), f"{(risk_stats['medio'] / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["Riesgo alto", str(risk_stats["alto"]), f"{(risk_stats['alto'] / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["", "", ""],
                ["ANÁLISIS POR TIPO DE CONTENIDO", "", ""],
                ["Análisis de texto", str(content_stats["texto"]), f"{(content_stats['texto'] / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"],
                ["Análisis de imagen", str(content_stats["imagen"]), f"{(content_stats['imagen'] / total_analyses * 100 if total_analyses > 0 else 0):.1f}%"]
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
                ("FONTNAME", (0, 10), (-1, 10), "Helvetica-Bold"),
                ("BACKGROUND", (0, 5), (-1, 5), colors.lightgrey),
                ("BACKGROUND", (0, 10), (-1, 10), colors.lightgrey),
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 30))

        if report_config["include_details"] and analyses:
            story.append(Paragraph("DETALLE DE ANÁLISIS", subtitle_style))

            for i, analysis in enumerate(analyses[:20]):
                story.append(Paragraph(f"Análisis #{i + 1}", styles["Heading3"]))

                detail_data = [
                    ["Fecha:", analysis.timestamp.strftime("%d/%m/%Y %H:%M")],
                    ["Tipo de contenido:", analysis.content_type.title()],
                    ["Nivel de riesgo:", analysis.risk_level.title()],
                    ["¿Es grooming?:", "Sí" if analysis.is_grooming else "No"],
                ]

                if analysis.signals_detected:
                    signals = json.loads(analysis.signals_detected)
                    if signals:
                        detail_data.append(["Señales detectadas:", ", ".join(signals)])

                if analysis.explanation:
                    explanation = analysis.explanation
                    if len(explanation) > 200:
                        explanation = explanation[:200] + "..."
                    detail_data.append(["Explicación:", explanation])

                detail_table = Table(detail_data, colWidths=[1.5 * inch, 4.5 * inch])
                detail_table.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ]))

                story.append(detail_table)
                story.append(Spacer(1, 15))

        if report_config["include_recommendations"]:
            story.append(Paragraph("RECOMENDACIONES DE SEGURIDAD", subtitle_style))
            recommendations = [
                "Mantener comunicación abierta con menores sobre sus actividades online",
                "Revisar regularmente la configuración de privacidad en redes sociales",
                "Educar sobre los riesgos del grooming y cómo identificarlos",
                "Establecer reglas claras sobre el uso de internet y dispositivos",
                "Supervisar las interacciones online, especialmente con desconocidos",
                "Utilizar herramientas de control parental cuando sea apropiado",
                "Reportar inmediatamente cualquier comportamiento sospechoso",
                "Mantener actualizados los sistemas de seguridad"
            ]
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", styles["Normal"]))
                story.append(Spacer(1, 8))

        story.append(Spacer(1, 30))
        story.append(Paragraph("_______________________________________________", styles["Normal"]))
        story.append(Paragraph("Este reporte fue generado automáticamente por SafeGuard v2.0", styles["Normal"]))
        story.append(Paragraph("Información confidencial - Uso exclusivo del usuario autorizado", styles["Normal"]))

        doc.build(story)
        pdf_buffer.seek(0)

        filename = f"safeguard_advanced_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": f"Error generando PDF avanzado: {str(e)}"}), 500

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Analysis": Analysis,
        "UserActivity": UserActivity,
        "TrustedContact": TrustedContact,
        "ChatSimulation": ChatSimulation
    }
if __name__ == "__main__":
    create_tables()
    app.run(debug=True, host="0.0.0.0", port=5000)
