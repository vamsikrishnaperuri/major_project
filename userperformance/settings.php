<?php
defined('MOODLE_INTERNAL') || die();

if ($ADMIN->fulltree) {
    $settings->add(new admin_setting_heading(
        'gradereport_userperformance_settings',
        get_string('pluginname', 'gradereport_userperformance'),
        'Configure user performance report settings.'
    ));
}
