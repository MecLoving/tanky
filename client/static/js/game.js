class HexRenderer {
    constructor(canvasId, hexSize = 40) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.hexSize = hexSize;
        this.colors = {
            grass: '#4CAF50',
            water: '#2196F3',
            mountain: '#795548',
            tankRed: '#F44336',
            tankBlue: '#2196F3',
            highlight: '#FFEB3B'
        };
    }

    drawHexGrid(mapData) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw terrain
        Object.entries(mapData).forEach(([coords, terrain]) => {
            const [q, r] = coords.split(',').map(Number);
            this.drawHex(q, r, this.colors[terrain]);
        });
    }

    drawHex(q, r, color) {
        const center = this.hexToPixel(q, r);
        this.ctx.beginPath();
        
        for (let i = 0; i < 6; i++) {
            const angle = Math.PI / 3 * i + Math.PI / 6;
            const x = center.x + this.hexSize * Math.cos(angle);
            const y = center.y + this.hexSize * Math.sin(angle);
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        
        this.ctx.fillStyle = color;
        this.ctx.fill();
        this.ctx.strokeStyle = '#000';
        this.ctx.stroke();
    }

    drawTanks(tanks) {
        tanks.forEach(tank => {
            const center = this.hexToPixel(tank.position.q, tank.position.r);
            const color = tank.playerId === 'player1' ? this.colors.tankRed : this.colors.tankBlue;
            
            // Draw tank base
            this.ctx.beginPath();
            this.ctx.arc(center.x, center.y, this.hexSize * 0.4, 0, Math.PI * 2);
            this.ctx.fillStyle = color;
            this.ctx.fill();
            this.ctx.stroke();
            
            // Draw tank ID
            this.ctx.fillStyle = '#FFF';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(tank.id.toString(), center.x, center.y);
            
            // Draw star if reached end
            if (tank.hasReachedEnd) {
                this.drawStar(center.x, center.y);
            }
        });
    }

    hexToPixel(q, r) {
        const x = this.hexSize * 3/2 * q;
        const y = this.hexSize * Math.sqrt(3) * (r + q/2);
        return {
            x: x + this.canvas.width / 2,
            y: y + this.canvas.height / 2
        };
    }

    drawStar(cx, cy, spikes=5, outerRadius=15, innerRadius=7) {
        let rot = Math.PI / 2 * 3;
        let x = cx;
        let y = cy;
        const step = Math.PI / spikes;

        this.ctx.beginPath();
        this.ctx.moveTo(cx, cy - outerRadius);
        
        for (let i = 0; i < spikes; i++) {
            x = cx + Math.cos(rot) * outerRadius;
            y = cy + Math.sin(rot) * outerRadius;
            this.ctx.lineTo(x, y);
            rot += step;

            x = cx + Math.cos(rot) * innerRadius;
            y = cy + Math.sin(rot) * innerRadius;
            this.ctx.lineTo(x, y);
            rot += step;
        }
        
        this.ctx.lineTo(cx, cy - outerRadius);
        this.ctx.closePath();
        this.ctx.fillStyle = '#FFD700';
        this.ctx.fill();
    }
}