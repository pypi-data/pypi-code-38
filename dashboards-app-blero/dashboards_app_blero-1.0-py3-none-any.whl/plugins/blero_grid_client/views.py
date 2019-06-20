
from .models import *
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt



import os
from dashboards_app.blero_utils.client_utils.logging_helpers import BleroLogger

cwd=os.path.dirname(os.path.realpath(__file__))+"/"
logger=BleroLogger(path=cwd,source=__name__)


@csrf_exempt
def save_grid(request):

    try:



        # change label to is edited



        row_values=request.POST.getlist('row_values[]')
        col_values=request.POST.getlist('col_values[]')

        logger.logger.debug(row_values)
        logger.logger.debug(col_values)
        model_id=request.POST['model_id']
        n_rows=len(row_values)
        n_columns=len(col_values)
        grid_values=[request.POST.getlist('grid_values['+str(i)+'][]') for i in range(n_rows)]



        #change edited to model
        active_grid=BleroGrid.objects.get(pk=model_id)
        active_grid.content_edited=True
        active_grid.save()

        #get cell values
        #GridCells
        for row in range(n_rows):

            row_content=row_values[row]
            temp_cell, created = GridRows.objects.update_or_create(model=active_grid, row_number=row,

                                                                    defaults={
                                                                        'content_edited': True,
                                                                        'row_content': row_content,
                                                                    }
                                                                    )

            for column in range(n_columns):


                #update Cell
                cell_value=grid_values[row][column]
                if cell_value !='':
                    temp_cell, created = GridCells.objects.update_or_create(model=active_grid,row_number= row, column_number= column,
                                                                            defaults={
                                                                                'content_edited': True,
                                                                                'cell_content': cell_value,
                                                                            }
                                                                            )

                    temp_cell.refresh_from_db()

        logger.debug("Grid values updatd")

    except Exception as e:
        logger.exception("error from view")

    return JsonResponse("ok", safe=False)
