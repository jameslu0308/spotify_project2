from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

with DAG(
    dag_id = 'dummy',
    start_date = datetime(2024,5,2),
    schedule_interval = None
) as dag:
    with TaskGroup(group_id = 'my_task_group') as tg1:
        task_1 = EmptyOperator(task_id = 'task_1')
        task_2 = EmptyOperator(task_id = 'task_2')
        task_3 = EmptyOperator(task_id = 'task_3')


        task_1 >> task_2 >> task_3


    start_task = EmptyOperator(task_id = 'start_task')
    end_task = EmptyOperator(task_id = 'end_task')

    start_task >> tg1 >> end_task




""" 
Q:
1. Can you accecpt yourself if you keep working in nanya?
even if it's because you want to study abroad.
-->  I want to try going to interview, 
    and see how I am perceived and valued in workplace nowadays.
    Even if I don't get a new job right away or in a near future,
    I think  I can accept that after I actually try. 
    
    It seems like actually doing something, try build new things or
    at least have some effort to step out of my current environment 
    is the most important thing for me right now.

    Because I can get some kind of fresh air , and even if I don't get 
    a new job. I enter a new process, and think I can be happier and lighter.
    At least one thing I can be sure of is mentally I will feel better, 
    because I try.

    So, the conclusion is clear, quickly get your resume sorted and start applying!

    The next question is , if you get a new job, go or don't go ?
    After which month, you should consider whether to accept the offer
    even if you have aced the interview with a new company.

    But, the next question is the next question.
    Right now is right now, afterward is afterward.
    Attempt to break free from the mindset of 
    keep worrying the things that havn't happened yet.

    If things really unfold that way, deal with it then;
    focusing on what you want to do now is what's most important.
    And then you should consider what to do if the worst-case scenario happens,
    how to protect myself, and what safeguards to put in place. 
    Case closed!!    

Happiness:

Reality:


 """
