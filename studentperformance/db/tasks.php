<?php
defined('MOODLE_INTERNAL') || die();

$tasks = [
    [
        'classname' => 'local_studentperformance\task\update_performance_data',
        'blocking' => 0,
        'minute' => '0',
        'hour' => '0',
        'day' => '*',
        'month' => '*',
        'dayofweek' => '*',
        'disabled' => 0
    ]
];