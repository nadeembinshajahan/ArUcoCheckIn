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

    // Initialize edge lines if not already present
    if (verticalLines.length === 0) {
        verticalLines = [
            { x: 0, name: 'Left Edge' },
            { x: containerWidth, name: 'Right Edge' }
        ];
    } else {
        // Update right edge position on resize
        verticalLines[verticalLines.length - 1].x = containerWidth;
    }

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

    // Insert new line at the correct position
    let insertIndex = 1; // Start after left edge
    while (insertIndex < verticalLines.length && verticalLines[insertIndex].x < x) {
        insertIndex++;
    }

    // Add line to storage
    verticalLines.splice(insertIndex, 0, {
        x: x,
        name: `Region ${insertIndex}`
    });

    // Redraw all lines and update regions
    redrawLines();
    updateRegionsTable();
});

function drawVerticalLine(x, isEdge = false) {
    drawCtx.beginPath();
    drawCtx.moveTo(x, 0);
    drawCtx.lineTo(x, drawCanvas.height);
    drawCtx.strokeStyle = isEdge ? '#ff0000' : '#00ff00'; // Red for edges, green for user lines
    drawCtx.lineWidth = isEdge ? 3 : 2;
    drawCtx.stroke();
}

function redrawLines() {
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    verticalLines.forEach((line, index) => {
        // Draw edges in red, other lines in green
        drawVerticalLine(line.x, index === 0 || index === verticalLines.length - 1);
    });
}

function updateRegionsTable() {
    const tbody = document.getElementById('regionsTable');
    // Create regions between consecutive lines
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
                ${region.id === 1 || region.id === regions.length ? '' : 
                    `<button class="btn btn-sm btn-danger" onclick="deleteRegion(${region.id})">Delete</button>`}
            </td>
        </tr>
    `).join('');
}

function updateRegionName(id, newName) {
    // Update the name of the right boundary line of the region
    if (id > 0 && id < verticalLines.length) {
        verticalLines[id].name = newName;
    }
}

function deleteRegion(id) {
    // Remove the line that separates this region (keep edges)
    if (id > 1 && id < verticalLines.length - 1) {
        verticalLines.splice(id, 1);
        redrawLines();
        updateRegionsTable();
    }
}

// Button handlers
document.getElementById('startDrawing').addEventListener('click', function(e) {
    this.classList.toggle('active');
});

document.getElementById('clearDrawing').addEventListener('click', function() {
    // Reset to just edge lines
    verticalLines = [
        { x: 0, name: 'Left Edge' },
        { x: drawCanvas.width, name: 'Right Edge' }
    ];
    redrawLines();
    updateRegionsTable();
});

document.getElementById('saveRegions').addEventListener('click', async function() {
    try {
        // Create regions from all lines
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