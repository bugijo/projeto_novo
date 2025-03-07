class Particle {
    constructor(canvas, x, y) {
        this.canvas = canvas;
        this.x = x;
        this.y = y;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = '#6c5ce7';
        this.alpha = Math.random() * 0.5 + 0.1;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.size > 0.2) this.size -= 0.1;

        // Bounce off edges
        if (this.x < 0 || this.x > this.canvas.width) {
            this.speedX *= -1;
        }
        if (this.y < 0 || this.y > this.canvas.height) {
            this.speedY *= -1;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(108, 92, 231, ${this.alpha})`;
        ctx.fill();
    }
}

class ParticleSystem {
    constructor() {
        this.canvas = document.getElementById('particles');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.isAnimating = false;
        this.mouseX = 0;
        this.mouseY = 0;

        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    handleMouseMove(e) {
        this.mouseX = e.x;
        this.mouseY = e.y;
        
        // Criar partículas na posição do mouse
        for (let i = 0; i < 3; i++) {
            this.particles.push(new Particle(this.canvas, this.mouseX, this.mouseY));
        }
    }

    start() {
        if (!this.isAnimating) {
            this.isAnimating = true;
            this.animate();
        }
    }

    stop() {
        this.isAnimating = false;
    }

    animate() {
        if (!this.isAnimating) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Atualizar e desenhar partículas
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            particle.update();
            particle.draw(this.ctx);

            // Remover partículas muito pequenas
            if (particle.size <= 0.2) {
                this.particles.splice(i, 1);
            }
        }

        // Adicionar novas partículas aleatoriamente
        if (this.particles.length < 100) {
            this.particles.push(new Particle(
                this.canvas,
                Math.random() * this.canvas.width,
                Math.random() * this.canvas.height
            ));
        }

        // Conectar partículas próximas
        this.connectParticles();

        requestAnimationFrame(() => this.animate());
    }

    connectParticles() {
        const maxDistance = 100;
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < maxDistance) {
                    const alpha = (1 - distance / maxDistance) * 0.2;
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(108, 92, 231, ${alpha})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }
}

// Iniciar sistema de partículas quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    const particleSystem = new ParticleSystem();
    particleSystem.start();
}); 