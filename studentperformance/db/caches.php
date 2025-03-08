<?php
defined('MOODLE_INTERNAL') || die();

$caches = [
    'performance_data' => [
        'mode' => cache_store::MODE_APPLICATION,
        'simplekeys' => true,
        'invalidationevents' => [
            'local_studentperformance_data_updated'
        ]
    ]
];