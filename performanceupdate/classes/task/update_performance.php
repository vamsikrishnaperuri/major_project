<?php
// classes/task/update_performance.php
namespace local_performanceupdate\task;

use \core\task\scheduled_task;

class update_performance extends scheduled_task {
    public function get_name() {
        return get_string('update_performance', 'local_performanceupdate');
    }

    public function execute() {
        global $CFG;

        // Define the paths to your Python scripts.
        $script1 = $CFG->dirroot . '/local/performanceupdate/scripts/first_script.py';
        $script2 = $CFG->dirroot . '/local/performanceupdate/scripts/second_script.py';

        // Execute the first script.
        $output1 = [];
        $return_var1 = 0;
        exec("python $script1", $output1, $return_var1);
        if ($return_var1 !== 0) {
            mtrace("Error executing first_script.py: " . implode("\n", $output1));
        } else {
            mtrace("first_script.py executed successfully.");
        }

        // Execute the second script.
        $output2 = [];
        $return_var2 = 0;
        exec("python $script2", $output2, $return_var2);
        if ($return_var2 !== 0) {
            mtrace("Error executing second_script.py: " . implode("\n", $output2));
        } else {
            mtrace("second_script.py executed successfully.");
        }
    }
}
