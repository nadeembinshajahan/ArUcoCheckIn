let videoCanvas = document.getElementById('videoCanvas');
let drawCanvas = document.getElementById('drawCanvas');
let videoCtx = videoCanvas.getContext('2d');
let drawCtx = drawCanvas.getContext('2d');

let isDrawing = false;
let startX, startY;
let regions = [];  // Store box regions
let streamUrl = null;

// Generate a unique color for each region
function generateUniqueColor() {
    // Generate vibrant colors using HSL
    const hue = (regions.length * 137.508) % 360; // Golden angle approximation
    return `hsl(${hue}, 70%, 50%)`;
}

// Set canvas size
function setCanvasSize() {
    const containerWidth = document.querySelector('.canvas-container').offsetWidth;
    const aspectRatio = 9/16;
    const height = containerWidth * aspectRatio;

    videoCanvas.width = drawCanvas.width = containerWidth;
    videoCanvas.height = drawCanvas.height = height;

    // Redraw regions after resize
    redrawRegions();
}

// Initialize
setCanvasSize();
window.addEventListener('resize', setCanvasSize);

// Drawing handlers for boxes
drawCanvas.addEventListener('mousedown', function(e) {
    if (!document.getElementById('startDrawing').classList.contains('active')) return;

    isDrawing = true;
    const rect = drawCanvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
});

drawCanvas.addEventListener('mousemove', function(e) {
    if (!isDrawing) return;

    const rect = drawCanvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    // Clear canvas and redraw all regions
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    redrawRegions();

    // Draw current box
    drawBox(startX, startY, currentX - startX, currentY - startY, '#00ff00');
});

drawCanvas.addEventListener('mouseup', function(e) {
    if (!isDrawing) return;

    const rect = drawCanvas.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    // Add new region with unique color
    regions.push({
        id: Date.now(),
        name: `Region ${regions.length + 1}`,
        x: Math.min(startX, endX),
        y: Math.min(startY, endY),
        width: Math.abs(endX - startX),
        height: Math.abs(endY - startY),
        color: generateUniqueColor()
    });

    isDrawing = false;
    updateRegionsTable();
});

function drawBox(x, y, width, height, color) {
    drawCtx.beginPath();
    drawCtx.rect(x, y, width, height);
    drawCtx.strokeStyle = color;
    drawCtx.lineWidth = 2;
    drawCtx.stroke();
}

function redrawRegions() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    regions.forEach(region => {
        drawBox(region.x, region.y, region.width, region.height, region.color);
    });
}

function updateRegionsTable() {
    const tbody = document.getElementById('regionsTable');
    tbody.innerHTML = regions.map(region => `
        <tr>
            <td>${region.id}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div style="width: 20px; height: 20px; background-color: ${region.color}; margin-right: 10px; border: 1px solid #666;"></div>
                    <input type="text" class="form-control" value="${region.name}"
                        onchange="updateRegionName('${region.id}', this.value)">
                </div>
            </td>
            <td>X: ${Math.round(region.x)}, Y: ${Math.round(region.y)}, 
                W: ${Math.round(region.width)}, H: ${Math.round(region.height)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteRegion('${region.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

function updateRegionName(id, newName) {
    const region = regions.find(r => r.id === parseInt(id));
    if (region) {
        region.name = newName;
    }
}

function deleteRegion(id) {
    regions = regions.filter(r => r.id !== parseInt(id));
    redrawRegions();
    updateRegionsTable();
}

// Button handlers
document.getElementById('startDrawing').addEventListener('click', function() {
    this.classList.toggle('active');
});

document.getElementById('clearDrawing').addEventListener('click', function() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    regions = [];
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
                regions: regions
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