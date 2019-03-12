import time
import requests
import logging
import settings
import tasks
# from vision.pi.server import start_threads

TASKS_DEBUG = {
    'MOVE': tasks.AbstractMoveTask,
    'PICKUP': tasks.AbstractPickupTask,
    'HANDOVER': tasks.AbstractHandoverTask
}

TASKS_REAL = {
    'MOVE': tasks.MoveTask,
    'PICKUP': tasks.PickupTask,
    'HANDOVER': tasks.HandoverTask
}

GROUP_TASKS = ['MOVE']


class MainControl:
    """
    This is the main controller for all the other modules.
    It does following:

    - grabs plan from the server API
    - executes the plan one step at a time
    - for each step of the plan it will invoke appropriate function and give it full control.
    - the control resumes if the tasks succeeds or fails.
    - after it finishes executing the plan it will start polling the server for new plan.
    """

    current_plan = None
    plan_grouped = []

    if settings.DEBUG:
        tasks_handlers = TASKS_DEBUG
    else:
        tasks_handlers = TASKS_REAL

    def get_plan(self):
        r = requests.get(settings.API_CURRENT_PLAN_URL)
        r.raise_for_status()

        if r.status_code == 204:
            return

        self.current_plan = r.json()
        self.group_plan()
        logging.info('Fetched a plan')

    def update_plan(self, data):
        r = requests.patch(
            settings.API_DETAIL_PLAN_URL.format(self.current_plan['id']),
            data=data,
            headers=settings.AUTH_HEADERS
        )
        r.raise_for_status()

    def loop(self):
        while True:
            if not self.current_plan:
                logging.info('Retrieving plan')
                self.get_plan()

            if not self.current_plan:
                logging.info('Waiting for a plan')
                time.sleep(1)
            else:
                self.execute_plan()

    def group_plan(self):
        """
        Move tasks are special - we should execute all following moves at once
        """
        self.plan_grouped = []

        current_group = None
        current_tasks = []
        for step in self.current_plan['steps']:
            if not current_group:
                current_group = step['action']

            if current_group == step['action']:
                current_tasks.append(step)
            else:
                self.plan_grouped.append(current_tasks)
                current_group = step['action']
                current_tasks = [step]

    def execute_group(self, action, group_data):
        task_class = self.tasks_handlers[action]
        task = task_class(group_data)
        task.run()
        return task

    def execute_plan(self):
        for group in self.plan_grouped:
            action = group[0]['action']
            task = self.execute_group(action, group)
            last_id = group[-1]['sub_id']
            logging.info('Executing {0}'.format(action))
            if task.success:
                self.report_success(last_id)
            else:
                self.report_failure(last_id)
                break

        self.update_plan({'state': 'finished'})
        self.current_plan = None


    def report_success(self, sub_id):
        logging.info('Task {0} succeeded.'.format(sub_id))
        self.update_plan({'steps_executed': sub_id})

    def report_failure(self, sub_id):
        logging.error('Task {0} failed.'.format(sub_id))

        self.update_plan({
            'steps_executed': sub_id,
            'state': 'aborted'
        })
        self.current_plan = None


if __name__ == '__main__':
    logging.info("Starting control loop")
    logging.info("Starting camera thread")
    #
    # start_threads()

    MainControl().loop()
