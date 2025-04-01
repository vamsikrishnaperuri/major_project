<?php
namespace block_chatbot;

use Exception;

class gemini_client {
    private $api_key;
    // private $api_url = 'https://api.openai.com/v1/chat/completions';
    private $api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';


    public function __construct($api_key) {
        $this->api_key = $api_key;
    }

    public function get_response($prompt) {
        $data = [
            'contents' => [
                [
                    'parts' => [
                        ['text' => $prompt]
                    ]
                ]
            ]
        ];
    
        $ch = curl_init($this->api_url . '?key=' . $this->api_key);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    
        $response = curl_exec($ch);
        if (curl_errno($ch)) {
            throw new Exception('Request Error: ' . curl_error($ch));
        }
        curl_close($ch);
    
        $result = json_decode($response, true);
        
        // Debugging purpose (optional)
        file_put_contents(__DIR__.'/debug.log', $response); 
    
        if (isset($result['candidates'][0]['content']['parts'][0]['text'])) {
            return $result['candidates'][0]['content']['parts'][0]['text'];
        } else {
            return 'No valid response from AI.';
        }
    }
    
}
