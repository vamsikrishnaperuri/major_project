<?php
require_once(__DIR__ . '/../../config.php');
require_login();

$context = context_system::instance();
require_capability('local/chatbot:view', $context);

// Ensure the request is an AJAX request
if (!is_ajax_request()) {
    throw new moodle_exception('invalidrequest', 'core_error');
}

// Set up the response header
header('Content-Type: application/json');

// Retrieve the POST data
$input = json_decode(file_get_contents('php://input'), true);
$user_message = trim($input['message'] ?? '');

if (empty($user_message)) {
    echo json_encode(['response' => 'Please enter a message.']);
    exit;
}

// Send the message to Flask backend
$flask_url = 'http://192.168.55.104:5000/chatbot'; // Change to your Flask server URL

$ch = curl_init($flask_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['message' => $user_message]));
$response = curl_exec($ch);

if (curl_errno($ch)) {
    $error_msg = curl_error($ch);
    echo json_encode(['response' => "Error communicating with chatbot: $error_msg"]);
    curl_close($ch);
    exit;
}

curl_close($ch);

// Return Flask response back to Moodle UI
echo $response;
exit;
?>
