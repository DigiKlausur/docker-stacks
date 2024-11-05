from e2xgrader.config import configure_base
from nbgrader.preprocessors import GetGrades
from nbformat import NotebookNode
from nbconvert.exporters.exporter import ResourcesDict
from nbgrader.api import MissingEntry
from nbconvert.preprocessors import CSSHTMLHeaderPreprocessor
from e2xgrader.preprocessors import FilterTests

from e2xgrader.graders import MultipleChoiceGrader, CodeGrader, SingleChoiceGrader
from e2xgrader.utils.extra_cells import get_choices, get_instructor_choices
from traitlets import Unicode

class GetGradesWithUngradedComment(GetGrades):
    """
    If a cell has not been graded, this processor adds a comment 
    saying "Unbewertet" to the cell
    """

    ungraded_comment = Unicode(
        "Unbewertet",
        help="Comment to add to ungraded cells"
    ).tag(config=True)
    
    def _get_comment(self, cell: NotebookNode, resources: ResourcesDict) -> None:
        """Graders can optionally add comments to the student's solutions, so
        add the comment information into the database if it doesn't
        already exist. It should NOT overwrite existing comments that
        might have been added by a grader already.

        """
        comment = self.gradebook.find_comment(
            cell.metadata['nbgrader']['grade_id'],
            self.notebook_id,
            self.assignment_id,
            self.student_id)
        
        needs_manual_grade = False
        try:        
            grade = self.gradebook.find_grade(
                cell.metadata['nbgrader']['grade_id'],
                self.notebook_id,
                self.assignment_id,
                self.student_id)
            needs_manual_grade = grade.needs_manual_grade
        except MissingEntry:
            pass
        
        comment = comment.comment
        
        if comment is None:
            comment = ""
        else:
            comment += "\n"

        # save it in the notebook
        if needs_manual_grade:
            cell.metadata.nbgrader['comment'] = comment + self.ungraded_comment
        else:
            cell.metadata.nbgrader['comment'] = comment
            

class WuSMultipleChoiceGrader(MultipleChoiceGrader):
    
    def determine_grade(self, cell, log=None):
        '''
        Grader for multiple choice questions
        
        Only give full points if student did select all correct 
        answers and no incorrect answers
        '''
        max_points = float(cell.metadata['nbgrader']['points'])
        student_choices = get_choices(cell)
        instructor_choices = get_instructor_choices(cell)
        
        # Return 0 points if the student did not select all correct answers
        for choice in instructor_choices:
            if choice not in student_choices:
                return 0, max_points
            
        # Return 0 points if the student did select an incorrect answer
        for choice in student_choices:
            if choice not in instructor_choices:
                return 0, max_points
            
        return max_points, max_points       
            
c = get_config() # noqa: F821

c.GenerateFeedback.preprocessors = [
    GetGradesWithUngradedComment,
    FilterTests,
    CSSHTMLHeaderPreprocessor
]

#print("Local config is", c)

c.SaveAutoGrades.graders = {
    'multiplechoice': WuSMultipleChoiceGrader(),
    'code': CodeGrader(),
    'singlechoice': SingleChoiceGrader()
}

