const canvas = document.getElementById('circleCanvas');
const ctx = canvas.getContext('2d');
const center = { x: canvas.width / 2, y: canvas.height / 2 };
const centerRadius = 10;
let isDrawing = false;
let points = [];
const drawSound = document.getElementById("drawSound");
const endSound = document.getElementById("endSound");


const scoreSpan = document.getElementById("score");
const bestScoreSpan = document.getElementById("bestScore");
const feedback = document.getElementById("feedback");


let bestScore = sessionStorage.getItem("bestCircleScore") || 0;
bestScoreSpan.textContent = bestScore + "%";


function drawCenterDot() {
  ctx.save();
  ctx.shadowColor = "#ff3939";
  ctx.shadowBlur = 24;
  ctx.fillStyle = 'red';
  ctx.beginPath();
  ctx.arc(center.x, center.y, centerRadius, 0, 2 * Math.PI);
  ctx.fill();
  ctx.restore();
}


canvas.addEventListener('mousedown', () => {
  isDrawing = true;
  points = [];
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCenterDot();
  feedback.textContent = "";
  scoreSpan.textContent = "0%";
  drawSound.currentTime = 0;
  drawSound.play();
});

canvas.addEventListener('mousemove', (e) => {
  if (!isDrawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  points.push({ x, y });
  drawLoop();
});

canvas.addEventListener('mouseup', () => {
  isDrawing = false;
  drawSound.pause();
  endSound.currentTime = 0;
  endSound.play();
  if (points.length >= 10) {
    if (isPointInPath(center, points)) {
      const score = scoreCircle(points, center);
      showScore(score);
      scoreSpan.textContent = score + "%";
      if (score > bestScore) {
        bestScore = score;
        sessionStorage.setItem("bestCircleScore", score);
        bestScoreSpan.textContent = score + "%";
        feedback.innerHTML = `<span style="color:#0af600;font-size:1.2em;">New Best!</span>`;
      } else {
        feedback.textContent = '';
      }
    } else {
      scoreSpan.textContent = "0%";
      feedback.innerHTML = `<span style="color:#ff3939;font-size:2em;">The red dot is not inside your circle!</span>`;
    }
  }
});

function drawLoop() {
  if (points.length < 2) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCenterDot();


  let grd = ctx.createLinearGradient(points[0].x, points[0].y, points[points.length - 1].x, points[points.length - 1].y);
  grd.addColorStop(0, "#ff3939"); 
  grd.addColorStop(0.5, "#fcff42"); 
  grd.addColorStop(1, "#1ff924"); 
  ctx.strokeStyle = grd;
  ctx.lineWidth = 5;
  ctx.shadowColor = "#fcff42";
  ctx.shadowBlur = 18;
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i].x, points[i].y);
  }
  ctx.stroke();
  ctx.shadowBlur = 0;
}


function isPointInPath(center, pts) {
  let count = 0;
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i], b = pts[i + 1];
    if (((a.y > center.y) !== (b.y > center.y)) &&
        (center.x < (b.x - a.x) * (center.y - a.y) / (b.y - a.y) + a.x)) {
      count++;
    }
  }
  return count % 2 === 1;
}


function scoreCircle(pts, center) {
  const ds = pts.map(p => Math.hypot(p.x - center.x, p.y - center.y));
  const avg = ds.reduce((a, b) => a + b, 0) / ds.length;
  const variance = ds.reduce((sum, d) => sum + Math.pow(d - avg, 2), 0) / ds.length;
  const score = Math.max(100 - Math.sqrt(variance) * 7, 5);
  return Math.round(score * 10) / 10;
}

function showScore(score) {
  scoreSpan.classList.add('animated-score');
  scoreSpan.style.transform = "scale(1.2)";
  setTimeout(() => { scoreSpan.style.transform = 'scale(1)' }, 300);
}


document.getElementById('resetBtn').onclick = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCenterDot();
  feedback.textContent = "";
  scoreSpan.textContent = "0%";
};


drawCenterDot();


