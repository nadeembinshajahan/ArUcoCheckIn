let videoCanvas = document.getElementById('videoCanvas');
let drawCanvas = document.getElementById('drawCanvas');
let videoCtx = videoCanvas.getContext('2d');
let drawCtx = drawCanvas.getContext('2d');

let isDrawing = false;
let currentPath = [];
let savedRegions = [];
let streamUrl = null;

// Set canvas size
function setCanvasSize() {
    const containerWidth = document.querySelector('.canvas-container').offsetWidth;
    const aspectRatio = 9/16;
    const height = containerWidth * aspectRatio;
    
    videoCanvas.width = drawCanvas.width = containerWidth;
    videoCanvas.height = drawCanvas.height = height;
}

// Initialize
setCanvasSize();
window.addEventListener('resize', setCanvasSize);

// Drawing handlers
drawCanvas.addEventListener('mousedown', startDraw);
drawCanvas.addEventListener('mousemove', draw);
drawCanvas.addEventListener('mouseup', endDraw);
drawCanvas.addEventListener('mouseout', endDraw);

function startDraw(e) {
    if (!document.getElementById('startDrawing').classList.contains('active')) return;
    
    isDrawing = true;
    const rect = drawCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    currentPath = [{x, y}];
    drawCtx.beginPath();
    drawCtx.moveTo(x, y);
    drawCtx.strokeStyle = '#00ff00';
    drawCtx.lineWidth = 2;
}

function draw(e) {
    if (!isDrawing) return;
    
    const rect = drawCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    currentPath.push({x, y});
    drawCtx.lineTo(x, y);
    drawCtx.stroke();
}

function endDraw() {
    if (!isDrawing) return;
    
    isDrawing = false;
    if (currentPath.length > 2) {
        // Close the path
        drawCtx.lineTo(currentPath[0].x, currentPath[0].y);
        drawCtx.stroke();
        drawCtx.closePath();
        
        // Add to saved regions
        savedRegions.push({
            id: Date.now(),
            name: `Artwork ${savedRegions.length + 1}`,
            points: currentPath
        });
        
        updateRegionsTable();
    }
    currentPath = [];
}

function updateRegionsTable() {
    const tbody = document.getElementById('regionsTable');
    tbody.innerHTML = savedRegions.map(region => `
        <tr>
            <td>${region.id}</td>
            <td>
                <input type="text" class="form-control" value="${region.name}"
                    onchange="updateRegionName(${region.id}, this.value)">
            </td>
            <td>${region.points.length} points</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteRegion(${region.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function updateRegionName(id, newName) {
    const region = savedRegions.find(r => r.id === id);
    if (region) {
        region.name = newName;
    }
}

function deleteRegion(id) {
    savedRegions = savedRegions.filter(r => r.id !== id);
    redrawRegions();
    updateRegionsTable();
}

function redrawRegions() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    
    savedRegions.forEach(region => {
        drawCtx.beginPath();
        drawCtx.moveTo(region.points[0].x, region.points[0].y);
        region.points.forEach(point => {
            drawCtx.lineTo(point.x, point.y);
        });
        drawCtx.lineTo(region.points[0].x, region.points[0].y);
        drawCtx.strokeStyle = '#00ff00';
        drawCtx.lineWidth = 2;
        drawCtx.stroke();
        drawCtx.closePath();
    });
}

// Button handlers
document.getElementById('startDrawing').addEventListener('click', function(e) {
    this.classList.toggle('active');
});

document.getElementById('clearDrawing').addEventListener('click', function() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    savedRegions = [];
    updateRegionsTable();
});

document.getElementById('saveRegions').addEventListener('click', async function() {
    try {
        const response = await fetch('/api/save_regions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                camera_url: streamUrl,
                regions: savedRegions
            })
        });
        
        if (response.ok) {
            alert('Regions saved successfully!');
        } else {
            alert('Failed to save regions');
        }
    } catch (error) {
        console.error('Error saving regions:', error);
        alert('Error saving regions');
    }
});

// Camera form handler
document.getElementById('cameraForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    streamUrl = document.getElementById('cameraUrl').value;
    
    try {
        const response = await fetch('/api/connect_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                camera_url: streamUrl
            })
        });
        
        if (response.ok) {
            // Start video stream
            const videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment'
                }
            });
            
            const video = document.createElement('video');
            video.srcObject = videoStream;
            video.play();
            
            // Update canvas with video feed
            function updateCanvas() {
                if (video.readyState === video.HAVE_ENOUGH_DATA) {
                    videoCtx.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height);
                }
                requestAnimationFrame(updateCanvas);
            }
            updateCanvas();
        } else {
            alert('Failed to connect to camera');
        }
    } catch (error) {
        console.error('Error connecting to camera:', error);
        alert('Error connecting to camera');
    }
});
