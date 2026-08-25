// SafeGuard JS

class SafeGuardUI {
    constructor() {
        this.initializeModals();
        this.initializeAnimations();
        this.initializeInteractivity();
    }

    initializeModals() {
        if (!document.getElementById('sg-modal-container')) {
            const container = document.createElement('div');
            container.id = 'sg-modal-container';
            container.innerHTML = `
                <div class="sg-modal-overlay" id="sg-modal-overlay">
                    <div class="sg-modal" id="sg-modal">
                        <div class="sg-modal-header">
                            <h5 class="sg-modal-title" id="sg-modal-title"></h5>
                            <button class="sg-modal-close" id="sg-modal-close">&times;</button>
                        </div>
                        <div class="sg-modal-body" id="sg-modal-body"></div>
                        <div class="sg-modal-footer" id="sg-modal-footer"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(container);
        }

        // Agregar estilos de modal
        this.addModalStyles();
        this.bindModalEvents();
    }

    // Estilos para modales personalizados
    addModalStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .sg-modal-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(8px);
                display: none;
                justify-content: center;
                align-items: flex-start;
                z-index: 10000;
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                padding: 2rem 1rem;
                overflow-y: auto;
            }
            
            .sg-modal-overlay.show {
                display: flex;
                opacity: 1;
            }
            
            .sg-modal {
                background: white;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(50, 50, 93, 0.25), 0 15px 35px rgba(0, 0, 0, 0.15);
                max-width: 560px;
                width: 100%;
                max-height: calc(100vh - 4rem);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                margin: auto 0;
                transform: translateY(30px) scale(0.96);
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                animation: modalSlideIn 0.3s ease forwards;
            }
                        
            @keyframes modalSlideIn {
                from {
                    transform: translateY(50px) scale(0.9);
                    opacity: 0;
                }
                to {
                    transform: translateY(0) scale(1);
                    opacity: 1;
                }
            }
            
            .sg-modal-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-shrink: 0;
            }
            
            .sg-modal-title {
                margin: 0;
                font-size: 1.3rem;
                font-weight: 600;
            }
            
            .sg-modal-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.8rem;
                cursor: pointer;
                opacity: 0.8;
                transition: opacity 0.2s;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
            }
            
            .sg-modal-close:hover {
                opacity: 1;
                background: rgba(255, 255, 255, 0.2);
            }
            
            .sg-modal-body {
                padding: 1.75rem;
                line-height: 1.6;
                flex: 1 1 auto;
                overflow-y: auto;
                min-height: 0;
                max-height: calc(100vh - 220px);
            }
            .sg-modal-body p,
            .sg-modal-body li,
            .sg-modal-body div,
            .sg-modal-body span {
                overflow-wrap: anywhere;
                word-break: break-word;
            }
            .sg-modal-footer {
                padding: 1.5rem;
                border-top: 1px solid #eee;
                display: flex;
                justify-content: flex-end;
                gap: 10px;
                flex-shrink: 0;
                background: white;
            }
            
            .sg-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                display: block;
                text-align: center;
            }
            .sg-modal-body::-webkit-scrollbar {
                    width: 8px;
                }

                .sg-modal-body::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 10px;
                }

                .sg-modal-body::-webkit-scrollbar-thumb {
                    background: rgba(102, 126, 234, 0.5);
                    border-radius: 10px;
                }

                .sg-modal-body::-webkit-scrollbar-thumb:hover {
                    background: rgba(102, 126, 234, 0.8);
                }
            .sg-icon.success { color: #28a745; }
            .sg-icon.warning { color: #ffc107; }
            .sg-icon.error { color: #dc3545; }
            .sg-icon.info { color: #17a2b8; }
            
            @media (max-width: 768px) {
                .sg-modal-overlay {
                    padding: 1rem 0.75rem;
                }

                .sg-modal {
                    width: 100%;
                    max-height: calc(100vh - 2rem);
                    border-radius: 16px;
                }
                
                .sg-modal-body {
                    padding: 1.25rem;
                    max-height: calc(100vh - 180px);
                }

                .sg-modal-header,
                .sg-modal-footer {
                    padding: 1rem 1.25rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Eventos de modal
    bindModalEvents() {
        const overlay = document.getElementById('sg-modal-overlay');
        const closeBtn = document.getElementById('sg-modal-close');

        // Cerrar modal al hacer clic en overlay
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeModal();
            }
        });

        // Cerrar modal con botón X
        closeBtn.addEventListener('click', () => {
            this.closeModal();
        });

        // Cerrar modal con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    // Mostrar modal personalizado
    showModal(options) {
        const {
            title = 'Notificación',
            message = '',
            type = 'info', // success, warning, error, info
            buttons = [{ text: 'OK', class: 'btn-primary', action: null }],
            icon = true
        } = options;

        const overlay = document.getElementById('sg-modal-overlay');
        const titleEl = document.getElementById('sg-modal-title');
        const bodyEl = document.getElementById('sg-modal-body');
        const footerEl = document.getElementById('sg-modal-footer');

        // Configurar título
        titleEl.textContent = title;

        // Configurar contenido
        let iconHtml = '';
        if (icon) {
            const icons = {
                success: 'fas fa-check-circle',
                warning: 'fas fa-exclamation-triangle',
                error: 'fas fa-times-circle',
                info: 'fas fa-info-circle'
            };
            iconHtml = `<i class="sg-icon ${type} ${icons[type]}"></i>`;
        }

        bodyEl.innerHTML = iconHtml + message;

        // Configurar botones
        footerEl.innerHTML = '';
        buttons.forEach(button => {
            const btn = document.createElement('button');
            btn.textContent = button.text;
            btn.className = `btn ${button.class || 'btn-secondary'}`;
            btn.addEventListener('click', () => {
                if (button.action) {
                    button.action();
                }
                this.closeModal();
            });
            footerEl.appendChild(btn);
        });

        // Mostrar modal
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    // Cerrar modal
    closeModal() {
        const overlay = document.getElementById('sg-modal-overlay');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    // Inicializar animaciones
    initializeAnimations() {
        // Intersection Observer para animaciones al hacer scroll
        if ('IntersectionObserver' in window) {
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fadeInUp');
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            // Observar elementos con clase 'animate-on-scroll'
            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                observer.observe(el);
            });
        }
    }

    //  interactividad
    initializeInteractivity() {
        // Smooth scrolling para enlaces internos
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Efecto de ondas en botones
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function (e) {
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;

                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.5);
                    border-radius: 50%;
                    pointer-events: none;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                `;

                button.appendChild(ripple);

                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });

        // Agregar estilos para efecto ripple
        const rippleStyle = document.createElement('style');
        rippleStyle.textContent = `
            .btn {
                position: relative;
                overflow: hidden;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(rippleStyle);
    }

    // Métodos de utilidad para reemplazar alerts del navegador
    alert(message, title = 'Aviso') {
        this.showModal({
            title,
            message,
            type: 'info',
            buttons: [{ text: 'OK', class: 'btn-primary' }]
        });
    }

    confirm(message, title = 'Confirmar', onConfirm = null) {
        this.showModal({
            title,
            message,
            type: 'warning',
            buttons: [
                { text: 'Cancelar', class: 'btn-secondary' },
                { text: 'Confirmar', class: 'btn-primary', action: onConfirm }
            ]
        });
    }

    success(message, title = 'Éxito') {
        this.showModal({
            title,
            message,
            type: 'success',
            buttons: [{ text: 'OK', class: 'btn-success' }]
        });
    }

    error(message, title = 'Error') {
        this.showModal({
            title,
            message,
            type: 'error',
            buttons: [{ text: 'OK', class: 'btn-danger' }]
        });
    }

    warning(message, title = 'Advertencia') {
        this.showModal({
            title,
            message,
            type: 'warning',
            buttons: [{ text: 'Entendido', class: 'btn-warning' }]
        });
    }
}

// Quiz interactivo mejorado
class InteractiveQuiz {
    constructor(containerId, questions) {
        this.container = document.getElementById(containerId);
        this.questions = questions;
        this.currentQuestion = 0;
        this.answers = {};
        this.score = 0;
        this.init();
    }

    init() {
        this.renderQuestion();
    }

    renderQuestion() {
        const question = this.questions[this.currentQuestion];
        const progressPercent = ((this.currentQuestion + 1) / this.questions.length) * 100;

        this.container.innerHTML = `
            <div class="quiz-container">
                <div class="quiz-progress mb-4">
                    <div class="progress">
                        <div class="progress-bar" style="width: ${progressPercent}%"></div>
                    </div>
                    <small class="text-muted mt-1">Pregunta ${this.currentQuestion + 1} de ${this.questions.length}</small>
                </div>
                
                <div class="quiz-question fadeInUp">
                    <h4 class="mb-4">${question.question}</h4>
                    <div class="quiz-options">
                        ${question.options.map((option, index) => `
                            <div class="quiz-option" data-value="${option.value}">
                                <div class="d-flex align-items-center">
                                    <i class="fas fa-circle-check me-3" style="opacity: 0.3;"></i>
                                    <span>${option.text}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="quiz-navigation mt-4">
                        ${this.currentQuestion > 0 ?
                '<button class="btn btn-secondary me-2" id="prev-btn"><i class="fas fa-arrow-left me-2"></i>Anterior</button>' :
                ''
            }
                        <button class="btn btn-primary" id="next-btn" disabled>
                            ${this.currentQuestion < this.questions.length - 1 ?
                'Siguiente<i class="fas fa-arrow-right ms-2"></i>' :
                'Finalizar Quiz<i class="fas fa-check ms-2"></i>'
            }
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.bindQuizEvents();
    }

    bindQuizEvents() {
        const options = this.container.querySelectorAll('.quiz-option');
        const nextBtn = this.container.querySelector('#next-btn');
        const prevBtn = this.container.querySelector('#prev-btn');

        options.forEach(option => {
            option.addEventListener('click', () => {
                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');

                const icon = option.querySelector('i');
                options.forEach(opt => {
                    opt.querySelector('i').style.opacity = '0.3';
                    opt.querySelector('i').style.color = '';
                });
                icon.style.opacity = '1';
                icon.style.color = '#667eea';

                this.answers[`q${this.currentQuestion}`] = option.dataset.value;
                nextBtn.disabled = false;
            });
        });

        nextBtn.addEventListener('click', () => {
            if (this.currentQuestion < this.questions.length - 1) {
                this.currentQuestion++;
                this.renderQuestion();
            } else {
                this.finishQuiz();
            }
        });

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.currentQuestion--;
                this.renderQuestion();
            });
        }
    }

    finishQuiz() {
        // Calcular puntuación
        let correct = 0;
        this.questions.forEach((question, index) => {
            if (this.answers[`q${index}`] === question.correct) {
                correct++;
            }
        });

        const percentage = Math.round((correct / this.questions.length) * 100);

        // Mostrar resultados
        this.showResults(correct, this.questions.length, percentage);

        // Enviar datos al servidor
        this.submitQuiz(this.answers, correct, percentage);
    }

    showResults(correct, total, percentage) {
        let message = '';
        let type = 'info';

        if (percentage >= 90) {
            message = `¡Excelente! Has respondido correctamente ${correct} de ${total} preguntas (${percentage}%). Tienes muy buenos conocimientos sobre seguridad en línea.`;
            type = 'success';
        } else if (percentage >= 70) {
            message = `¡Bien hecho! Has respondido correctamente ${correct} de ${total} preguntas (${percentage}%). Tienes buenos conocimientos, pero puedes mejorar un poco más.`;
            type = 'info';
        } else if (percentage >= 50) {
            message = `Regular. Has respondido correctamente ${correct} de ${total} preguntas (${percentage}%). Es importante que repases la información de seguridad.`;
            type = 'warning';
        } else {
            message = `Necesitas mejorar. Has respondido correctamente ${correct} de ${total} preguntas (${percentage}%). Te recomendamos repasar el material educativo.`;
            type = 'error';
        }

        window.safeguard.showModal({
            title: 'Resultados del Quiz',
            message: message,
            type: type,
            buttons: [{
                text: 'Ver Material Educativo',
                class: 'btn-info',
                action: () => window.location.href = '/kids/learn'
            }, {
                text: 'Cerrar',
                class: 'btn-primary'
            }]
        });
    }

    submitQuiz(answers, correct, percentage) {
        fetch('/api/quiz/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: answers,
                quiz_type: 'safety',
                score: percentage
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log('Quiz enviado exitosamente:', data);
            })
            .catch(error => {
                console.error('Error enviando quiz:', error);
            });
    }
}

// Simulador de chat seguro
class SafeChatSimulator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scenarios = this.getScenarios();
        this.currentScenario = 0;
        this.userResponses = [];
        this.init();
    }

    getScenarios() {
        return [
            {
                name: "Desconocido Amigable",
                difficulty: "Fácil",
                description: "Un extraño se acerca de manera amigable pero hace preguntas sospechosas",
                messages: [
                    { sender: "stranger", text: "¡Hola! Me gustaron tus fotos, eres muy guapo/a 😊", isRed: false },
                    { sender: "stranger", text: "¿Cuántos años tienes? ¿En qué escuela estudias?", isRed: true },
                    { sender: "stranger", text: "Me gustaría conocerte mejor, ¿tienes WhatsApp?", isRed: true }
                ],
                responses: [
                    { text: "Gracias, no doy información personal", safe: true, explanation: "Correcto: Nunca compartas información personal con desconocidos." },
                    { text: "Tengo 14 años y estudio en...", safe: false, explanation: "Peligroso: Estás dando información que puede usarse para localizarte." },
                    { text: "No hablo con desconocidos", safe: true, explanation: "Correcto: Es una respuesta directa y segura." }
                ]
            },
            {
                name: "Oferta de Regalo",
                difficulty: "Medio",
                description: "Alguien ofrece regalos y pide guardar secretos",
                messages: [
                    { sender: "stranger", text: "Te vi en el parque ayer, eres muy linda/o", isRed: true },
                    { sender: "stranger", text: "¿Te gustaría que te regale algo especial?", isRed: true },
                    { sender: "stranger", text: "Pero no le digas a tus papás, será nuestro secreto 🤫", isRed: true }
                ],
                responses: [
                    { text: "No acepto regalos de desconocidos", safe: true, explanation: "Correcto: Los regalos de extraños pueden ser una trampa." },
                    { text: "¡Sí, me encantan los regalos!", safe: false, explanation: "Peligroso: Los depredadores usan regalos para ganar confianza." },
                    { text: "Voy a contarle a mis padres", safe: true, explanation: "Excelente: Siempre involucra a tus padres cuando alguien pide secretos." }
                ]
            },
            {
                name: "Solicitud de Fotos",
                difficulty: "Medio",
                description: "Un contacto solicita fotos personales de manera gradual",
                messages: [
                    { sender: "stranger", text: "Hemos hablado mucho, me siento como si te conociera", isRed: false },
                    { sender: "stranger", text: "¿Podrías enviarme una foto tuya? Solo para verte mejor", isRed: true },
                    { sender: "stranger", text: "No tiene que ser nada raro, solo una foto normal 📸", isRed: true }
                ],
                responses: [
                    { text: "No envío fotos a personas que no conozco", safe: true, explanation: "Correcto: Las fotos pueden ser mal utilizadas." },
                    { text: "Ok, te envío una foto normal", safe: false, explanation: "Peligroso: Cualquier foto puede ser usada inadecuadamente." },
                    { text: "¿Por qué necesitas mi foto?", safe: true, explanation: "Buena pregunta: Cuestionar las intenciones es importante." }
                ]
            },
            {
                name: "Encuentro Físico",
                difficulty: "Difícil",
                description: "Alguien intenta coordinar un encuentro en persona",
                messages: [
                    { sender: "stranger", text: "Hemos hablado tanto que siento que eres mi mejor amigo/a", isRed: false },
                    { sender: "stranger", text: "¿Te gustaría que nos encontremos en persona?", isRed: true },
                    { sender: "stranger", text: "Podemos vernos en el centro comercial, no le digas a nadie 😉", isRed: true }
                ],
                responses: [
                    { text: "No me encuentro con personas que conocí en línea", safe: true, explanation: "Perfecto: Nunca te encuentres solo con desconocidos de internet." },
                    { text: "Sí, pero solo si van mis padres", safe: true, explanation: "Buena opción: Si hay supervisión adulta puede ser seguro." },
                    { text: "¡Sí! Será divertido", safe: false, explanation: "Muy peligroso: Los encuentros secretos con desconocidos son extremadamente riesgosos." }
                ]
            },
            {
                name: "Manipulación Emocional",
                difficulty: "Difícil",
                description: "Uso de chantaje emocional y manipulación",
                messages: [
                    { sender: "stranger", text: "Estoy pasando por un momento muy difícil...", isRed: false },
                    { sender: "stranger", text: "Eres la única persona que me entiende y me ayuda", isRed: true },
                    { sender: "stranger", text: "Si realmente me quieres, harías esto por mí... ¿verdad?", isRed: true }
                ],
                responses: [
                    { text: "Siento que estés mal, pero no puedo ayudarte así", safe: true, explanation: "Correcto: Puedes ser empático sin ponerte en riesgo." },
                    { text: "Claro, haré lo que me pidas", safe: false, explanation: "Peligroso: La manipulación emocional es una táctica común de grooming." },
                    { text: "Creo que deberías hablar con un adulto", safe: true, explanation: "Excelente: Redirigir a ayuda profesional es lo correcto." }
                ]
            },
            {
                name: "Información de Rutina",
                difficulty: "Medio",
                description: "Preguntas aparentemente inocentes sobre tu rutina diaria",
                messages: [
                    { sender: "stranger", text: "¿A qué hora sales de la escuela normalmente?", isRed: true },
                    { sender: "stranger", text: "¿Siempre tomas la misma ruta a casa?", isRed: true },
                    { sender: "stranger", text: "¿Hay días en que llegas solo/a a casa?", isRed: true }
                ],
                responses: [
                    { text: "Esa información es privada", safe: true, explanation: "Correcto: Tu rutina debe mantenerse privada." },
                    { text: "Salgo a las 3 PM y camino por...", safe: false, explanation: "Peligroso: Esta información puede usarse para acosarte." },
                    { text: "¿Por qué quieres saber eso?", safe: true, explanation: "Buena respuesta: Cuestionar las intenciones sospechosas." }
                ]
            }
        ];
    }

    init() {
        this.renderScenario();
    }

    renderScenario() {
        const scenario = this.scenarios[this.currentScenario];
        const progress = ((this.currentScenario + 1) / this.scenarios.length) * 100;

        this.container.innerHTML = `
            <div class="chat-simulator">
                <div class="chat-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-1">Simulador: ${scenario.name}</h5>
                            <small class="text-muted">${scenario.description}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-${this.getDifficultyColor(scenario.difficulty)}">${scenario.difficulty}</span>
                            <div class="mt-1">
                                <small class="text-muted">Escenario ${this.currentScenario + 1} de ${this.scenarios.length}</small>
                            </div>
                        </div>
                    </div>
                    <div class="progress mt-2" style="height: 4px;">
                        <div class="progress-bar bg-success" role="progressbar" style="width: ${progress}%"></div>
                    </div>
                </div>
                
                <div class="chat-messages" id="chat-messages">
                    ${scenario.messages.map((msg, index) => `
                        <div class="chat-message ${msg.sender} ${msg.isRed ? 'danger' : ''}" 
                             style="animation-delay: ${index * 0.5}s">
                            <div class="message-content">
                                ${msg.text}
                                ${msg.isRed ? '<i class="fas fa-exclamation-triangle text-danger ms-2" title="Señal de alerta"></i>' : ''}
                            </div>
                            <div class="message-time">hace unos segundos</div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="chat-responses">
                    <div class="d-flex align-items-center mb-3">
                        <i class="fas fa-reply text-primary me-2"></i>
                        <p class="fw-bold mb-0">¿Cómo responderías?</p>
                    </div>
                    <div class="response-options">
                        ${scenario.responses.map((response, index) => `
                            <button class="btn btn-outline-primary response-btn mb-2" 
                                    data-safe="${response.safe}" 
                                    data-index="${index}"
                                    data-explanation="${response.explanation}">
                                <i class="fas fa-comment me-2"></i>
                                ${response.text}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        this.bindChatEvents();
    }

    getDifficultyColor(difficulty) {
        const colors = {
            'Fácil': 'success',
            'Medio': 'warning',
            'Difícil': 'danger'
        };
        return colors[difficulty] || 'secondary';
    }

    bindChatEvents() {
        const responseButtons = this.container.querySelectorAll('.response-btn');

        responseButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const isSafe = e.target.dataset.safe === 'true';
                const index = parseInt(e.target.dataset.index);
                const explanation = e.target.dataset.explanation;

                this.userResponses.push({
                    scenario: this.currentScenario,
                    response: index,
                    safe: isSafe
                });

                this.showFeedback(isSafe, e.target.textContent.trim(), explanation);
            });
        });
    }

    showFeedback(isSafe, responseText, explanation) {
        const icon = isSafe ? '✅' : '⚠️';
        const title = isSafe ? 'Respuesta Segura' : 'Respuesta Peligrosa';
        const additionalTips = isSafe ?
            '<div class="mt-3"><strong>💡 Recuerda:</strong><ul><li>Siempre confía en tu instinto</li><li>Mantén la comunicación con tus padres</li><li>No compartas información personal</li></ul></div>' :
            '<div class="mt-3"><strong>🚨 Consejos de seguridad:</strong><ul><li>Bloquea a la persona inmediatamente</li><li>Cuenta a un adulto de confianza</li><li>Guarda evidencia de la conversación</li></ul></div>';

        window.safeguard.showModal({
            title: `${icon} ${title}`,
            message: `
                <div class="feedback-content">
                    <p class="lead">"${responseText}"</p>
                    <div class="alert alert-${isSafe ? 'success' : 'warning'} mb-3">
                        <strong>${explanation}</strong>
                    </div>
                    ${additionalTips}
                </div>
            `,
            type: isSafe ? 'success' : 'warning',
            buttons: [{
                text: this.currentScenario < this.scenarios.length - 1 ? 'Siguiente Escenario' : 'Ver Resultados',
                class: 'btn-primary',
                action: () => this.nextScenario()
            }]
        });
    }

    nextScenario() {
        if (this.currentScenario < this.scenarios.length - 1) {
            this.currentScenario++;
            this.renderScenario();
        } else {
            this.finishSimulation();
        }
    }

    finishSimulation() {
        const safeResponses = this.userResponses.filter(r => r.safe).length;
        const totalResponses = this.userResponses.length;
        const percentage = Math.round((safeResponses / totalResponses) * 100);

        let message = `Has completado la simulación. Elegiste respuestas seguras en ${safeResponses} de ${totalResponses} situaciones (${percentage}%).`;

        if (percentage >= 80) {
            message += " ¡Excelente! Tienes muy buena intuición para mantenerte seguro en línea.";
        } else {
            message += " Te recomendamos repasar las estrategias de seguridad.";
        }

        window.safeguard.success(message, 'Simulación Completada');

        // Guardar resultados
        this.saveSimulationResults(percentage);
    }

    saveSimulationResults(score) {
        fetch('/api/chat-simulation/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                responses: this.userResponses,
                score: score
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log('Simulación guardada:', data);
            })
            .catch(error => {
                console.error('Error guardando simulación:', error);
            });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    window.safeguard = new SafeGuardUI();

    window.originalAlert = window.alert;
    window.alert = function (message) {
        window.safeguard.alert(message);
    };

    window.originalConfirm = window.confirm;
    window.confirm = function (message, callback) {
        window.safeguard.confirm(message, 'Confirmar', callback);
        return false; // Prevenir el comportamiento default
    };

    document.querySelectorAll('.card, .alert, .btn').forEach(el => {
        el.classList.add('animate-on-scroll');
    });

    const quizContainer = document.getElementById('quiz-container');
    if (quizContainer) {
        const questions = [
            {
                question: "¿Qué debes hacer si un desconocido te pide información personal en línea?",
                options: [
                    { text: "Darle solo mi nombre", value: "nombre" },
                    { text: "No darle ninguna información", value: "nunca" },
                    { text: "Preguntarle por qué lo necesita", value: "preguntar" }
                ],
                correct: "nunca"
            },
            {
                question: "Si alguien te hace sentir incómodo/a en una conversación, ¿qué debes hacer?",
                options: [
                    { text: "Seguir hablando para ser educado/a", value: "seguir" },
                    { text: "Hablar con un adulto de confianza", value: "hablar_adulto" },
                    { text: "Ignorar la situación", value: "ignorar" }
                ],
                correct: "hablar_adulto"
            },
            {
                question: "¿Qué hacer si alguien te pide que guardes secretos de tus padres?",
                options: [
                    { text: "Guardar el secreto si es menor", value: "guardar" },
                    { text: "No responder y contarle a mis padres", value: "no_responder" },
                    { text: "Preguntar de qué se trata", value: "preguntar" }
                ],
                correct: "no_responder"
            },
            {
                question: "¿Cuáles son señales de grooming?",
                options: [
                    { text: "Solo los regalos", value: "regalos" },
                    { text: "Solo las preguntas personales", value: "preguntas" },
                    { text: "Regalos, secretos, preguntas personales y aislar de la familia", value: "todas" }
                ],
                correct: "todas"
            },
            {
                question: "¿Cuándo debes pedir ayuda a un adulto?",
                options: [
                    { text: "Solo cuando es muy grave", value: "grave" },
                    { text: "Inmediatamente si algo te hace sentir incómodo/a", value: "inmediatamente" },
                    { text: "Después de intentar resolverlo solo/a", value: "despues" }
                ],
                correct: "inmediatamente"
            }
        ];

        new InteractiveQuiz('quiz-container', questions);
    }

    const chatSimulator = document.getElementById('chat-simulator');
    if (chatSimulator) {
        new SafeChatSimulator('chat-simulator');
    }
});

// Funciones globales de utilidad
window.showSuccess = function (message, title) {
    window.safeguard.success(message, title);
};

window.showError = function (message, title) {
    window.safeguard.error(message, title);
};

window.showWarning = function (message, title) {
    window.safeguard.warning(message, title);
};

window.showInfo = function (message, title) {
    window.safeguard.alert(message, title);
};