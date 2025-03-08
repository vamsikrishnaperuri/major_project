<?php
namespace local_studentperformance\task;

defined('MOODLE_INTERNAL') || die();

class update_performance_data extends \core\task\scheduled_task {
    public function get_name() {
        return get_string('task_update_performance', 'local_studentperformance');
    }

    public function execute() {
        mtrace('Starting performance data update...');
        
        try {
            $performance_updater = new \local_studentperformance\performance_updater();
            $result = $performance_updater->update_performance_data();
            
            if ($result) {
                mtrace('Performance data updated successfully');
            } else {
                mtrace('Failed to update performance data');
            }
        } catch (\Exception $e) {
            mtrace('Error updating performance data: ' . $e->getMessage());
        }
    }
}