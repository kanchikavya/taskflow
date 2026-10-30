/**
 * TaskFlow Kanban Board
 * 
 * Manages client-side drag-and-drop and asynchronous status updates
 * by calling the REST API endpoint: PATCH /api/tasks/{id}/update-status/
 * without reloading the page.
 */

// Helper to retrieve Django's CSRF token from browser cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Shows a transient Bootstrap Toast notification
function showKanbanToast(message, type = 'success') {
    const toastEl = document.getElementById('kanbanToast');
    const toastBody = document.getElementById('kanbanToastBody');
    const toastHeader = document.getElementById('kanbanToastHeader');

    if (!toastEl || !toastBody) {
        alert(message);
        return;
    }

    toastBody.textContent = message;

    if (type === 'success') {
        toastHeader.className = 'toast-header bg-success text-white';
        toastHeader.querySelector('strong').textContent = 'Task Updated';
    } else {
        toastHeader.className = 'toast-header bg-danger text-white';
        toastHeader.querySelector('strong').textContent = 'Update Failed';
    }

    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
    toast.show();
}

// Recount tasks in all column headers and manage empty state placeholders
function updateColumnCounters() {
    const columns = ['todo', 'in_progress', 'done'];

    columns.forEach(status => {
        const columnList = document.querySelector(`.kanban-tasks-list[data-status="${status}"]`);
        const badge = document.getElementById(`count-${status}`);
        if (!columnList) return;

        const cards = columnList.querySelectorAll('.kanban-card');
        const count = cards.length;

        if (badge) {
            badge.textContent = count;
        }

        // Toggle empty placeholder visibility
        let placeholder = columnList.querySelector('.kanban-empty-placeholder');
        if (count === 0) {
            if (!placeholder) {
                placeholder = document.createElement('div');
                placeholder.className = 'kanban-empty-placeholder';
                placeholder.textContent = 'No tasks in this stage';
                columnList.appendChild(placeholder);
            }
        } else {
            if (placeholder) {
                placeholder.remove();
            }
        }
    });
}

// Asynchronously update task status via DRF REST API
async function performStatusUpdate(taskId, newStatus, cardElement, targetListElement) {
    const csrftoken = getCookie('csrftoken');
    const originalParent = cardElement.parentElement;
    const taskTitle = cardElement.getAttribute('data-task-title') || `Task #${taskId}`;

    // Optimistically update UI
    cardElement.style.opacity = '0.5';

    try {
        const response = await fetch(`/api/tasks/${taskId}/update-status/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            const errData = await response.json();
            const errMsg = errData.detail || errData.error || 'Server rejected the status update.';
            throw new Error(errMsg);
        }

        const data = await response.json();

        // Successful update: move card element to target column
        targetListElement.appendChild(cardElement);
        cardElement.setAttribute('data-current-status', newStatus);
        cardElement.style.opacity = '1';

        // Update column badge counts
        updateColumnCounters();

        const statusNames = {
            'todo': 'To Do',
            'in_progress': 'In Progress',
            'done': 'Done'
        };

        showKanbanToast(`"${taskTitle}" moved to ${statusNames[newStatus] || newStatus}`, 'success');

    } catch (error) {
        console.error('TaskFlow Kanban Error:', error);
        // Revert card to original column on error
        originalParent.appendChild(cardElement);
        cardElement.style.opacity = '1';
        updateColumnCounters();
        showKanbanToast(`Error: ${error.message}`, 'error');
    }
}

// Initialize Drag & Drop and Click Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    let draggedCard = null;

    // 1. Setup Draggable Cards
    const cards = document.querySelectorAll('.kanban-card');
    cards.forEach(card => {
        card.setAttribute('draggable', 'true');

        card.addEventListener('dragstart', (e) => {
            draggedCard = card;
            card.classList.add('is-dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', card.getAttribute('data-task-id'));
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('is-dragging');
            draggedCard = null;
        });
    });

    // 2. Setup Drop Zones (Columns)
    const dropZones = document.querySelectorAll('.kanban-tasks-list');
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', (e) => {
            // Only remove if leaving the actual zone container
            if (!zone.contains(e.relatedTarget)) {
                zone.classList.remove('drag-over');
            }
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');

            if (!draggedCard) return;

            const taskId = draggedCard.getAttribute('data-task-id');
            const targetStatus = zone.getAttribute('data-status');
            const currentStatus = draggedCard.getAttribute('data-current-status');

            // Only send API request if the column actually changed
            if (targetStatus && targetStatus !== currentStatus) {
                performStatusUpdate(taskId, targetStatus, draggedCard, zone);
            }
        });
    });

    // 3. Setup Quick Move Buttons (Dropdowns for Mobile & Accessibility)
    document.querySelectorAll('.btn-quick-move').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const taskId = button.getAttribute('data-task-id');
            const targetStatus = button.getAttribute('data-target-status');
            const card = document.querySelector(`.kanban-card[data-task-id="${taskId}"]`);
            const targetZone = document.querySelector(`.kanban-tasks-list[data-status="${targetStatus}"]`);

            if (card && targetZone) {
                performStatusUpdate(taskId, targetStatus, card, targetZone);
            }
        });
    });

    // Initial counter verification
    updateColumnCounters();
});
