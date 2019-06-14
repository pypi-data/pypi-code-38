import json

from app.core.db import DB


class DbTasks(DB):
    async def q1(self, name, task):
        sub_tasks = task.get('tasks', {})
        sql = """
            SELECT *
            FROM
                task_manager.tasks t
            WHERE
                NOT t.closed
            LIMIT 1
        """
        res = await self.query_all(sql)
        res = [dict(el) for el in res]
        return {
            "name": name,
            "ok": True,
            "tasks": sub_tasks,
            "result": res,
        }
    async def q2(self, name, task):
        sub_tasks = task.get('tasks', {})
        sql = """
            SELECT *
            FROM
                task_manager.tasks t
            WHERE
                NOT t.closed
            LIMIT 2
        """
        res = await self.query_all(sql)
        res = [dict(el) for el in res]
        return {
            "name": name,
            "ok": True,
            "tasks": sub_tasks,
            "result": res,
        }
    async def q3(self, name, task):
        sub_tasks = task.get('tasks', {})
        sql = """
            SELECT *
            FROM
                task_manager.tasks t
            WHERE
                NOT t.closed
            LIMIT 3
        """
        res = await self.query_all(sql)
        res = [dict(el) for el in res]
        return {
            "name": name,
            "ok": True,
            "tasks": sub_tasks,
            "result": res,
        }
