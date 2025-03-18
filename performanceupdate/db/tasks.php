<?php
// db/tasks.php
defined('MOODLE_INTERNAL') || die();

$tasks = [
    [
        'classname' => '\local_performanceupdate\task\update_performance',
        'blocking' => 0,
        'minute' => '0',
        'hour' => '0',
        'day' => '*',
        'month' => '*',
        'dayofweek' => '*',
    ],
];
