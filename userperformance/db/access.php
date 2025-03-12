<?php
$capabilities = [
    'gradereport/userperformance:view' => [
        'captype' => 'read',
        'contextlevel' => CONTEXT_COURSE,
        'archetypes' => ['teacher' => CAP_ALLOW, 'manager' => CAP_ALLOW],
    ],
];
