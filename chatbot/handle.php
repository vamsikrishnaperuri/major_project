<?php
require('../../config.php');
require_once($CFG->dirroot . '/blocks/chatbot/classes/gemini_client.php');
require_login();

$query = required_param('query', PARAM_TEXT);
$api_key = 'AIzaSyBHh8a7RMpIK9LrIgkXwf4sozLxibN1YcQ'; // Replace with your Gemini API key

$gemini = new \block_chatbot\gemini_client($api_key);
try {
    $response = $gemini->get_response($query);
} catch (Exception $e) {
    $response = 'Error: ' . $e->getMessage();
}

echo $response;
