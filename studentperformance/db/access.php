<?php
defined('MOODLE_INTERNAL') || die();

$capabilities = [
    'local/studentperformance:view' => [
        'captype' => 'read',
        'contextlevel' => CONTEXT_COURSE,
        'legacy' => [
            'guest' => CAP_ALLOW,
            'student' => CAP_ALLOW,
            'teacher' => CAP_ALLOW,
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW,
        ]
    ]
];