let videoCanvas = document.getElementById('videoCanvas');
let drawCanvas = document.getElementById('drawCanvas');
let videoCtx = videoCanvas.getContext('2d');
let drawCtx = drawCanvas.getContext('2d');

let verticalLines = [];  // Store x-coordinates of vertical lines
let streamUrl = null;

// Set canvas size
function setCanvasSize() {
    const containerWidth = document.querySelector('.canvas-container').offsetWidth;
    const aspectRatio = 9/16;
    const height = containerWidth * aspectRatio;

    videoCanvas.width = drawCanvas.width = containerWidth;
    videoCanvas.height = drawCanvas.height = height;

    // Redraw lines after resize
    redrawLines();
}

// Initialize
setCanvasSize();
window.addEventListener('resize', setCanvasSize);

// Drawing handler - now just for vertical lines
drawCanvas.addEventListener('click', function(e) {
    if (!document.getElementById('startDrawing').classList.contains('active')) return;

    const rect = drawCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;

    // Add line to storage
    verticalLines.push({
        x: x,
        name: `Region ${verticalLines.length + 1}`
    });

    // Draw the line
    drawVerticalLine(x);
    updateRegionsTable();
});

function drawVerticalLine(x) {
    drawCtx.beginPath();
    drawCtx.moveTo(x, 0);
    drawCtx.lineTo(x, drawCanvas.height);
    drawCtx.strokeStyle = '#00ff00';
    drawCtx.lineWidth = 2;
    drawCtx.stroke();
}

function redrawLines() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    verticalLines.forEach(line => {
        drawVerticalLine(line.x);
    });
}

function updateRegionsTable() {
    const tbody = document.getElementById('regionsTable');
    // Create regions from pairs of lines
    const regions = [];
    for (let i = 0; i < verticalLines.length - 1; i++) {
        regions.push({
            id: i + 1,
            name: `Region ${i + 1}`,
            start: verticalLines[i].x,
            end: verticalLines[i + 1].x
        });
    }

    tbody.innerHTML = regions.map(region => `
        <tr>
            <td>${region.id}</td>
            <td>
                <input type="text" class="form-control" value="${region.name}"
                    onchange="updateRegionName(${region.id}, this.value)">
            </td>
            <td>X: ${Math.round(region.start)} to ${Math.round(region.end)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteRegion(${region.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function updateRegionName(id, newName) {
    const region = verticalLines[id - 1];
    if (region) {
        region.name = newName;
    }
}

function deleteRegion(id) {
    // Remove the vertical lines that define this region
    verticalLines.splice(id - 1, 2);
    redrawLines();
    updateRegionsTable();
}

// Button handlers
document.getElementById('startDrawing').addEventListener('click', function(e) {
    this.classList.toggle('active');
});

document.getElementById('clearDrawing').addEventListener('click', function() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    verticalLines = [];
    updateRegionsTable();
});

document.getElementById('saveRegions').addEventListener('click', async function() {
    try {
        // Create regions from pairs of lines
        const regions = [];
        for (let i = 0; i < verticalLines.length - 1; i++) {
            regions.push({
                id: i + 1,
                name: verticalLines[i].name,
                boundaries: {
                    start: verticalLines[i].x,
                    end: verticalLines[i + 1].x
                }
            });
        }

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