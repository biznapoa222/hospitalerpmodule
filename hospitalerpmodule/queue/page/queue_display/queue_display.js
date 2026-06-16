frappe.pages['queue-display'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Queue Display',
        single_column: true
    });

    frappe.require('queue_display.css');
    $(wrapper).find('.page-head').hide();

    var container = $('<div class="queue-display-container"></div>').appendTo(wrapper);

    frappe.call({
        method: 'hospitalerpmodule.queue.page.queue_display.queue_display.get_hospital_name',
        callback: function(r) {
            var hospitalName = r.message || 'Hospital Queue System';
            renderQueueDisplay(container, hospitalName);
            refreshQueueDisplay(container, hospitalName);
            setInterval(function() {
                refreshQueueDisplay(container, hospitalName);
            }, 8000);
            updateClock();
            setInterval(updateClock, 1000);
        }
    });
};

function renderQueueDisplay(container, hospitalName) {
    var html = [
        '<div class="header">',
        '  <div class="hospital-name">' + hospitalName + '</div>',
        '  <div class="header-stats">',
        '    <div class="header-stat"><div class="label">Waiting</div><div class="value" id="total-waiting" style="color:#f59e0b">0</div></div>',
        '    <div class="header-stat"><div class="label">Completed</div><div class="value" id="total-completed" style="color:#34d399">0</div></div>',
        '    <div class="header-stat"><div class="label">Serving Now</div><div class="value" id="total-serving" style="color:#60a5fa">0</div></div>',
        '    <div class="clock"><div id="current-time">--:--:--</div><div class="date" id="current-date">---</div></div>',
        '  </div>',
        '</div>',
        '<div class="now-serving-banner" id="now-serving-banner" style="display:none">',
        '  <div><div class="now-serving-label">Now Serving</div><div class="now-serving-patient" id="banner-patient">---</div></div>',
        '  <div class="now-serving-token" id="banner-token">---</div>',
        '</div>',
        '<div class="counters-grid" id="counters-grid">',
        '  <div class="empty-queue" id="empty-state">',
        '    <div class="icon">🏥</div>',
        '    <div class="text">No active queues at the moment</div>',
        '  </div>',
        '</div>',
        '<div class="refresh-indicator">Auto-refreshing every 8s</div>'
    ].join('\n');

    container.html(html);
}

function refreshQueueDisplay(container, hospitalName) {
    frappe.call({
        method: 'hospitalerpmodule.queue.page.queue_display.queue_display.get_queue_data',
        callback: function(r) {
            if (r.message) {
                updateQueueUI(r.message, container);
            }
        }
    });
}

function updateQueueUI(data, container) {
    if (!data || !data.counters) return;

    var totalWaiting = 0;
    var totalCompleted = data.stats ? data.stats.total_completed || 0 : 0;
    var totalServing = 0;
    var firstServing = null;

    var countersHtml = '';
    data.counters.forEach(function(counter, index) {
        totalWaiting += counter.waiting_count || 0;
        var isServing = counter.currently_serving && counter.currently_serving.ticket_number !== '---';
        if (isServing) {
            totalServing++;
            if (!firstServing) firstServing = counter.currently_serving;
        }

        counter.counter_number = counter.counter_number || '';
        counter.location = counter.location || '';

        var token = isServing ? counter.currently_serving.ticket_number : '---';
        var patient = isServing ? counter.currently_serving.patient_name : '';

        var waitingHtml = '';
        if (counter.waiting && counter.waiting.length > 0) {
            counter.waiting.forEach(function(w) {
                var priorityClass = w.priority ? w.priority.toLowerCase() : 'normal';
                var waitTime = w.waiting_time_minutes !== null && w.waiting_time_minutes !== undefined ? w.waiting_time_minutes + ' min' : '--';
                waitingHtml += '<div class="waiting-item ' + priorityClass + '">' +
                    '<span class="token">' + w.ticket_number + '</span>' +
                    '<span class="name">' + (w.patient_name || '') + '</span>' +
                    '<span class="wait-time">' + waitTime + '</span>' +
                    '</div>';
            });
        } else {
            waitingHtml = '<div style="color:#64748b;font-size:13px;text-align:center;padding:10px">No patients waiting</div>';
        }

        countersHtml += '<div class="counter-card fade-in" style="animation-delay:' + (index * 0.05) + 's">' +
            '<div class="counter-header">' +
            '<div class="counter-name">' + counter.counter_name + '</div>' +
            '<div class="counter-number-badge">Counter ' + counter.counter_number + '</div>' +
            '</div>' +
            '<div class="serving-section">' +
            '<div class="serving-label">Currently Serving</div>' +
            '<div class="serving-token">' + token + '</div>' +
            '<div class="serving-name">' + patient + '</div>' +
            '</div>' +
            '<div class="waiting-section">' +
            '<h4>In Queue (' + (counter.waiting_count || 0) + ')</h4>' +
            '<div class="waiting-list">' + waitingHtml + '</div>' +
            '</div>' +
            '</div>';
    });

    if (countersHtml) {
        countersHtml = '<div style="display:contents">' + countersHtml + '</div>';
    }

    container.find('#counters-grid').html(countersHtml || '<div class="empty-queue"><div class="icon">🏥</div><div class="text">No active queues at the moment</div></div>');
    container.find('#total-waiting').text(totalWaiting);
    container.find('#total-completed').text(totalCompleted);
    container.find('#total-serving').text(totalServing);

    if (firstServing && firstServing.ticket_number && firstServing.ticket_number !== '---') {
        var banner = container.find('#now-serving-banner');
        banner.show();
        banner.find('#banner-token').text(firstServing.ticket_number);
        banner.find('#banner-patient').text(firstServing.patient_name || '');
    } else {
        container.find('#now-serving-banner').hide();
    }
}

function updateClock() {
    var now = new Date();
    var timeStr = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    var dateStr = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    $('#current-time').text(timeStr);
    $('#current-date').text(dateStr);
}
