async function loadDashboard() {
  try {
    const [health, summary, cameras, detections] = await Promise.all([
      fetch('/api/health').then(r => r.json()),
      fetch('/api/summary').then(r => r.json()),
      fetch('/api/cameras').then(r => r.json()),
      fetch('/api/detections?limit=20').then(r => r.json())
    ]);

    document.getElementById('systemStatus').textContent = health.status === 'online' ? 'System Online' : 'Offline';
    document.getElementById('statusDot').style.background = '#64e0a0';
    document.getElementById('studentsNow').textContent = summary.students_now ?? 0;
    document.getElementById('onlineCameras').textContent = summary.online_cameras ?? 0;
    document.getElementById('totalCameras').textContent = summary.cameras ?? 0;
    document.getElementById('lastDetection').textContent =
      summary.last_detection ? new Date(summary.last_detection).toLocaleTimeString() : '—';

    document.getElementById('cameras').innerHTML = cameras.length
      ? cameras.map(c => `
        <div class="camera">
          <div class="camera-title"><b>${escapeHtml(c.name)}</b><span class="${c.status==='online'?'online':'offline'}">${escapeHtml(c.status)}</span></div>
          <div class="muted">${escapeHtml(c.location)}</div>
          <strong>Camera ${c.camera_id}</strong>
          <small class="muted">${c.last_seen ? new Date(c.last_seen).toLocaleString() : 'No data yet'}</small>
        </div>`).join('')
      : '<div class="empty">No cameras registered. Start the worker.</div>';

    document.getElementById('detections').innerHTML = detections.length
      ? detections.map(d => `
        <tr><td>${new Date(d.detected_at).toLocaleTimeString()}</td>
        <td>${escapeHtml(d.camera_name || 'Camera '+d.camera_id)}</td>
        <td>${d.student_count}</td>
        <td>${Number(d.attention_score || 0).toFixed(1)}%</td>
        <td>${escapeHtml(d.mode)}</td></tr>`).join('')
      : '<tr><td colspan="5">No detection data yet.</td></tr>';
  } catch (error) {
    document.getElementById('systemStatus').textContent = 'Connection Error';
    document.getElementById('statusDot').style.background = '#ef8d8d';
    console.error(error);
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'
  }[c]));
}

if (document.getElementById('studentsNow')) {
  loadDashboard();
  setInterval(loadDashboard, 10000);
}
