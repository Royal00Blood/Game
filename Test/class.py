class StudentMarks:
    def __init__(self, data:dict):
        """
        data: словарь вида
        {
            'Ivanov':[5,6,2,None,'6']
            ...
        }
        """
        self.data=data
        self.clear_data = {}
        self.analyzer_data = {}
        
# Очистка данных
    def cleaner_data(self):
        '''
            Приводит оценки к int и удаляет некорректные значения
        '''
        for key, value in self.data.items():
            clean_grade = []
            
            for i in value:
                try:
                    a= int(i)
                    if 1<=a<=5:
                        clean_grade.append(a)
                except (ValueError,TypeError):
                    continue
            self.clear_data[key] = clean_grade
    
# Анализ данных
    def analyze(self):
        """
         Считает средний бал и статус
        """
        if not self.clear_data:
            self.cleaner_data()
        for key, grades in self.clear_data.items():
            if len(grades)==0:
                self.analyzer_data[key]={
                    "avg":None,
                    "status":"no data"
                }
                continue
            avg = sum(grades)/len(grades)
            self.analyzer_data[key]={
                    "avg":avg,
                    "status": "passed" if avg>=3 else "failed"
                }
        return self.analyzer_data
    
    def top_student(self, threshold = 4.5):
        """
        Формирует список  студентов с оценкой выше порога
        threshold: порог оценки
        """
        if not self.analyzer_data:
            self.analyze()
        
        return list(
            map(lambda x: x[0],
                filter(
                    lambda item: item[1]["avg"] is not None
                and item[1]["avg"]>=threshold,
                self.analyzer_data.items()
                )
                
            )
        )
         
f = {}                   
student_data = StudentMarks(f)
student_data.analyze() 
student_data.cleaner_data() 
student_data.top_student()  