class MatchmakingUI {
    constructor() {
        this.socket = io(); // Connect to SocketIO
        this.queueTime = 0;
        this.timerInterval = null;
        
        document.getElementById('join-queue').addEventListener('click', () => this.joinQueue());
    }

    joinQueue() {
        const button = document.getElementById('join-queue');
        const status = document.getElementById('queue-status');
        const timer = document.getElementById('queue-timer');
        
        // Visual feedback
        button.disabled = true;
        status.classList.remove('hidden');
        timer.classList.remove('hidden');
        
        // Start queue timer
        this.queueTime = 0;
        this.timerInterval = setInterval(() => {
            this.queueTime++;
            timer.textContent = `(${this.formatTime(this.queueTime)})`;
        }, 1000);
        
        // SocketIO event listeners
        this.socket.on('queue_update', (data) => {
            document.getElementById('status-text').textContent = data.message;
        });
        
        this.socket.on('match_found', () => {
            clearInterval(this.timerInterval);
            window.location.href = '/game';
        });
        
        // Send join request
        this.socket.emit('join_queue');
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    }
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    new MatchmakingUI();
});