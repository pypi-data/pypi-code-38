from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from votebase.core.statistics.views.graphs.matrix import GraphMatrixView
from votebase.core.statistics.views.graphs.thumbs import GraphThumbsView
from votebase.core.statistics.views.graphs.stars import GraphStarsView
from votebase.core.statistics.views.graphs.general import GraphsView, \
    GraphOptionsQuestionView, GraphTextvalueView, GraphsHashView
from votebase.core.statistics.views.exports import ExportCsvView, ExportPdfView
from votebase.core.statistics.views.infographics import InfographicsView, InfographicsHashView
from votebase.core.statistics.views.voters import VotersView, \
    VoterDeleteView, VoterView, PreGenerateQuizResults, GenerateQuizResults, \
    VotersNonQuizResults, VoterByHashView, VotingHistory, VoterHistoryView, VoterUpdateView

urlpatterns = [
    # graphs
    url(_(r'graphs/(?P<pk>[-\d]+)/$'), GraphsView.as_view(), name='statistics_graphs'),
    url(_(r'graphs/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphsView.as_view(), name='statistics_graphs_round'),
    url(_(r'graphs/segment/(?P<round_hash_key>[-\w]+)/$'), GraphsHashView.as_view(), name='statistics_graphs_hash_round'),
    url(_(r'graphs/survey/(?P<survey_hash_key>[-\w]+)/$'), GraphsHashView.as_view(), name='statistics_graphs_hash_survey'),

    # infographics
    url(_(r'infographics/(?P<pk>[-\d]+)/$'), InfographicsView.as_view(), name='statistics_infographics'),
    url(_(r'infographics/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), InfographicsView.as_view(), name='statistics_infographics_round'),
    url(_(r'infographics/segment/(?P<round_hash_key>[-\w]+)/$'), InfographicsHashView.as_view(), name='statistics_infographics_hash_round'),
    url(_(r'infographics/survey/(?P<survey_hash_key>[-\w]+)/$'), InfographicsHashView.as_view(), name='statistics_infographics_hash_survey'),

    # voters
    url(_(r'voters/to-fix/(?P<password>[-\w]+)/$'), VotersNonQuizResults.as_view(), name='statistics_voters_to_fix'),
    url(_(r'voters/generate-quiz-results/(?P<password>[-\w]+)/$'), GenerateQuizResults.as_view(), name='statistics_generate_quiz_results'),
    url(_(r'voters/pregenerate-quiz-results/(?P<round_pk>[-\d]+)/(?P<password>[-\w]+)/$'), PreGenerateQuizResults.as_view(), name='statistics_generate_quiz_results'),

    url(_(r'voters/delete/(?P<pk>[-\d]+)/$'), VoterDeleteView.as_view(), name='statistics_delete_voter'),
    url(_(r'voters/(?P<pk>[-\d]+)/$'), VotersView.as_view(), name='statistics_voters'),
    url(_(r'voters/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), VotersView.as_view(), name='statistics_voters_round'),
    url(_(r'voter/(?P<pk>[-\d]+)/edit/$'), VoterUpdateView.as_view(), name='statistics_voter_update'),
    url(_(r'voter/(?P<pk>[-\d]+)/$'), VoterView.as_view(), name='statistics_voter'),
    url(_(r'voter/result/(?P<hash_key>[-\w]+)/$'), VoterByHashView.as_view(), name='statistics_voter_hash'),
    url(_(r'voting/history/$'), VotingHistory.as_view(), name='statistics_voting_history'),
    url(_(r'history/voter/(?P<hash_key>[-\w]+)/$'), VoterHistoryView.as_view(), name='statistics_voter_history'),

    # cvs export
    url(_(r'export/csv/(?P<pk>[-\d]+)/$'), ExportCsvView.as_view(), name='statistics_export'),
    url(_(r'export/csv/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), ExportCsvView.as_view(), name='statistics_export_round'),

    # pdf export
    url(_(r'graphs/(?P<pk>[-\d]+)/export/pdf/$'), ExportPdfView.as_view(), name='statistics_export_pdf'),

    # radio
    url(_(r'graph/radio/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_radio_total'),
    url(_(r'graph/radio/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_radio_round'),

    # gender
    url(_(r'graph/gender/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_gender_total'),
    url(_(r'graph/gender/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_gender_round'),

    # checkbox
    url(_(r'graph/checkbox/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_checkbox_total'),
    url(_(r'graph/checkbox/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_checkbox_round'),

    # select single
    url(_(r'graph/select-single/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_select_single_total'),
    url(_(r'graph/select-single/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_select_single_round'),

    # select multiple
    url(_(r'graph/select-multiple/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_select_multiple_total'),
    url(_(r'graph/select-multiple/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_select_multiple_round'),

    # textfield
    url(_(r'graph/textfield/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_textfield_total'),
    url(_(r'graph/textfield/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_textfield_round'),

    # textarea
    url(_(r'graph/textarea/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_textarea_total'),
    url(_(r'graph/textarea/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_textarea_round'),

    # email
    url(_(r'graph/email/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_email_total'),
    url(_(r'graph/email/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_email_round'),

    # phone
    url(_(r'graph/phone/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_phone_total'),
    url(_(r'graph/phone/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_phone_round'),

    # date
    url(_(r'graph/date/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_date_total'),
    url(_(r'graph/date/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_date_round'),

    # time
    url(_(r'graph/time/(?P<pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_time_total'),
    url(_(r'graph/time/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphTextvalueView.as_view(), name='statistics_graph_time_round'),

    # matrix-radio
    url(_(r'graph/matrix-radio/(?P<pk>[-\d]+)/$'), GraphMatrixView.as_view(), name='statistics_graph_matrix_radio_total'),
    url(_(r'graph/matrix-radio/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphMatrixView.as_view(), name='statistics_graph_matrix_radio_round'),

    # matrix-checkbox
    url(_(r'graph/matrix-checkbox/(?P<pk>[-\d]+)/$'), GraphMatrixView.as_view(), name='statistics_graph_matrix_checkbox_total'),
    url(_(r'graph/matrix-checkbox/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphMatrixView.as_view(), name='statistics_graph_matrix_checkbox_round'),

    # true/false
    url(_(r'graph/true-false/(?P<pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_true_false_total'),
    url(_(r'graph/true-false/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphOptionsQuestionView.as_view(), name='statistics_graph_true_false_round'),

    # stars
    url(_(r'graph/stars/(?P<pk>[-\d]+)/$'), GraphStarsView.as_view(), name='statistics_graph_stars_total'),
    url(_(r'graph/stars/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphStarsView.as_view(), name='statistics_graph_stars_round'),

    # thumbs
    url(_(r'graph/thumbs/(?P<pk>[-\d]+)/$'), GraphThumbsView.as_view(), name='statistics_graph_thumbs_total'),
    url(_(r'graph/thumbs/(?P<pk>[-\d]+)/segment/(?P<round_pk>[-\d]+)/$'), GraphThumbsView.as_view(), name='statistics_graph_thumbs_round'),
]
