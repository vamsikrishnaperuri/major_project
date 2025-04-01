<?php
require_once(__DIR__ . '/../../config.php');
require_login();

$context = context_system::instance();
require_capability('local/chatbot:view', $context);

$PAGE->set_context($context);
$PAGE->set_url(new moodle_url('/local/chatbot/index.php'));
$PAGE->set_title(get_string('chatbot', 'local_chatbot'));
$PAGE->set_heading(get_string('chatbot', 'local_chatbot'));

echo $OUTPUT->header();
?>

<div id="chatbot-container">
    <div id="chatbot-messages"></div>
    <textarea id="chatbot-input" placeholder="Type your message here..."></textarea>
    <button id="chatbot-send">Send</button>
</div>

<style>
    #chatbot-container {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }
    #chatbot-messages {
        border: 1px solid #ccc;
        padding: 10px;
        height: 300px;
        overflow-y: scroll;
        margin-bottom: 10px;
    }
    #chatbot-input {
        width: 100%;
        padding: 10px;
    }
    #chatbot-send {
        padding: 10px 20px;
        margin-top: 10px;
    }
</style>

<script>
document.getElementById('chatbot-send').onclick = function() {
    const message = document.getElementById('chatbot-input').value;
    fetch('http://192.168.55.103:5000/chatbot', {  // <<< Replace HERE
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        const messages = document.getElementById('chatbot-messages');
        messages.innerHTML += '<div><strong>You:</strong> ' + message + '</div>';
        messages.innerHTML += '<div><strong>Bot:</strong> ' + data.response + '</div>';
        document.getElementById('chatbot-input').value = '';
    });
};
</script>


<?php
echo $OUTPUT->footer();
