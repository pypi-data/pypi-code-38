# Generated from antlr_tsql/tsql.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .tsqlParser import tsqlParser
else:
    from tsqlParser import tsqlParser

# This class defines a complete generic visitor for a parse tree produced by tsqlParser.

class tsqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by tsqlParser#tsql_file.
    def visitTsql_file(self, ctx:tsqlParser.Tsql_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#batch.
    def visitBatch(self, ctx:tsqlParser.BatchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sql_clauses.
    def visitSql_clauses(self, ctx:tsqlParser.Sql_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sql_clause.
    def visitSql_clause(self, ctx:tsqlParser.Sql_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#dml_clause.
    def visitDml_clause(self, ctx:tsqlParser.Dml_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#ddl_clause.
    def visitDdl_clause(self, ctx:tsqlParser.Ddl_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#block_statement.
    def visitBlock_statement(self, ctx:tsqlParser.Block_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#break_statement.
    def visitBreak_statement(self, ctx:tsqlParser.Break_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#continue_statement.
    def visitContinue_statement(self, ctx:tsqlParser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#goto_statement.
    def visitGoto_statement(self, ctx:tsqlParser.Goto_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#if_statement.
    def visitIf_statement(self, ctx:tsqlParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#return_statement.
    def visitReturn_statement(self, ctx:tsqlParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#throw_statement.
    def visitThrow_statement(self, ctx:tsqlParser.Throw_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#try_catch_statement.
    def visitTry_catch_statement(self, ctx:tsqlParser.Try_catch_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#waitfor_statement.
    def visitWaitfor_statement(self, ctx:tsqlParser.Waitfor_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#while_statement.
    def visitWhile_statement(self, ctx:tsqlParser.While_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#print_statement.
    def visitPrint_statement(self, ctx:tsqlParser.Print_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#raiseerror_statement.
    def visitRaiseerror_statement(self, ctx:tsqlParser.Raiseerror_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#another_statement.
    def visitAnother_statement(self, ctx:tsqlParser.Another_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#delete_statement.
    def visitDelete_statement(self, ctx:tsqlParser.Delete_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#delete_statement_from.
    def visitDelete_statement_from(self, ctx:tsqlParser.Delete_statement_fromContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#insert_statement.
    def visitInsert_statement(self, ctx:tsqlParser.Insert_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#insert_statement_value.
    def visitInsert_statement_value(self, ctx:tsqlParser.Insert_statement_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#select_statement.
    def visitSelect_statement(self, ctx:tsqlParser.Select_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#update_statement.
    def visitUpdate_statement(self, ctx:tsqlParser.Update_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#where_clause_dml.
    def visitWhere_clause_dml(self, ctx:tsqlParser.Where_clause_dmlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#output_clause.
    def visitOutput_clause(self, ctx:tsqlParser.Output_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#output_dml_list_elem.
    def visitOutput_dml_list_elem(self, ctx:tsqlParser.Output_dml_list_elemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#output_column_name.
    def visitOutput_column_name(self, ctx:tsqlParser.Output_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_database.
    def visitCreate_database(self, ctx:tsqlParser.Create_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_index.
    def visitCreate_index(self, ctx:tsqlParser.Create_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_statistics.
    def visitCreate_statistics(self, ctx:tsqlParser.Create_statisticsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_table.
    def visitCreate_table(self, ctx:tsqlParser.Create_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_view.
    def visitCreate_view(self, ctx:tsqlParser.Create_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#view_attribute.
    def visitView_attribute(self, ctx:tsqlParser.View_attributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#alter_table.
    def visitAlter_table(self, ctx:tsqlParser.Alter_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#alter_database.
    def visitAlter_database(self, ctx:tsqlParser.Alter_databaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#database_optionspec.
    def visitDatabase_optionspec(self, ctx:tsqlParser.Database_optionspecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#auto_option.
    def visitAuto_option(self, ctx:tsqlParser.Auto_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#change_tracking_option.
    def visitChange_tracking_option(self, ctx:tsqlParser.Change_tracking_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#change_tracking_option_list.
    def visitChange_tracking_option_list(self, ctx:tsqlParser.Change_tracking_option_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#containment_option.
    def visitContainment_option(self, ctx:tsqlParser.Containment_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#cursor_option.
    def visitCursor_option(self, ctx:tsqlParser.Cursor_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#date_correlation_optimization_option.
    def visitDate_correlation_optimization_option(self, ctx:tsqlParser.Date_correlation_optimization_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#db_encryption_option.
    def visitDb_encryption_option(self, ctx:tsqlParser.Db_encryption_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#db_state_option.
    def visitDb_state_option(self, ctx:tsqlParser.Db_state_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#db_update_option.
    def visitDb_update_option(self, ctx:tsqlParser.Db_update_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#db_user_access_option.
    def visitDb_user_access_option(self, ctx:tsqlParser.Db_user_access_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#delayed_durability_option.
    def visitDelayed_durability_option(self, ctx:tsqlParser.Delayed_durability_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#external_access_option.
    def visitExternal_access_option(self, ctx:tsqlParser.External_access_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#mixed_page_allocation_option.
    def visitMixed_page_allocation_option(self, ctx:tsqlParser.Mixed_page_allocation_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#parameterization_option.
    def visitParameterization_option(self, ctx:tsqlParser.Parameterization_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#recovery_option.
    def visitRecovery_option(self, ctx:tsqlParser.Recovery_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#service_broker_option.
    def visitService_broker_option(self, ctx:tsqlParser.Service_broker_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#snapshot_option.
    def visitSnapshot_option(self, ctx:tsqlParser.Snapshot_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sql_option.
    def visitSql_option(self, ctx:tsqlParser.Sql_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#target_recovery_time_option.
    def visitTarget_recovery_time_option(self, ctx:tsqlParser.Target_recovery_time_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#termination.
    def visitTermination(self, ctx:tsqlParser.TerminationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_index.
    def visitDrop_index(self, ctx:tsqlParser.Drop_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_procedure.
    def visitDrop_procedure(self, ctx:tsqlParser.Drop_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_statistics.
    def visitDrop_statistics(self, ctx:tsqlParser.Drop_statisticsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_table.
    def visitDrop_table(self, ctx:tsqlParser.Drop_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_view.
    def visitDrop_view(self, ctx:tsqlParser.Drop_viewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_type.
    def visitCreate_type(self, ctx:tsqlParser.Create_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#drop_type.
    def visitDrop_type(self, ctx:tsqlParser.Drop_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#rowset_function_limited.
    def visitRowset_function_limited(self, ctx:tsqlParser.Rowset_function_limitedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#openquery.
    def visitOpenquery(self, ctx:tsqlParser.OpenqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#opendatasource.
    def visitOpendatasource(self, ctx:tsqlParser.OpendatasourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#declare_statement.
    def visitDeclare_statement(self, ctx:tsqlParser.Declare_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#cursor_statement.
    def visitCursor_statement(self, ctx:tsqlParser.Cursor_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#execute_statement.
    def visitExecute_statement(self, ctx:tsqlParser.Execute_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#execute_statement_arg.
    def visitExecute_statement_arg(self, ctx:tsqlParser.Execute_statement_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#execute_var_string.
    def visitExecute_var_string(self, ctx:tsqlParser.Execute_var_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#security_statement.
    def visitSecurity_statement(self, ctx:tsqlParser.Security_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#grant_permission.
    def visitGrant_permission(self, ctx:tsqlParser.Grant_permissionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#set_statement.
    def visitSet_statement(self, ctx:tsqlParser.Set_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#transaction_statement.
    def visitTransaction_statement(self, ctx:tsqlParser.Transaction_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#go_statement.
    def visitGo_statement(self, ctx:tsqlParser.Go_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#use_statement.
    def visitUse_statement(self, ctx:tsqlParser.Use_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#execute_clause.
    def visitExecute_clause(self, ctx:tsqlParser.Execute_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#declare_local.
    def visitDeclare_local(self, ctx:tsqlParser.Declare_localContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_type_definition.
    def visitTable_type_definition(self, ctx:tsqlParser.Table_type_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_def_table_constraints.
    def visitColumn_def_table_constraints(self, ctx:tsqlParser.Column_def_table_constraintsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_def_table_constraint.
    def visitColumn_def_table_constraint(self, ctx:tsqlParser.Column_def_table_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_definition.
    def visitColumn_definition(self, ctx:tsqlParser.Column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_constraint.
    def visitColumn_constraint(self, ctx:tsqlParser.Column_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_constraint.
    def visitTable_constraint(self, ctx:tsqlParser.Table_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#index_options.
    def visitIndex_options(self, ctx:tsqlParser.Index_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#index_option.
    def visitIndex_option(self, ctx:tsqlParser.Index_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#declare_cursor.
    def visitDeclare_cursor(self, ctx:tsqlParser.Declare_cursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#declare_set_cursor_common.
    def visitDeclare_set_cursor_common(self, ctx:tsqlParser.Declare_set_cursor_commonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#fetch_cursor.
    def visitFetch_cursor(self, ctx:tsqlParser.Fetch_cursorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#set_special.
    def visitSet_special(self, ctx:tsqlParser.Set_specialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#constant_LOCAL_ID.
    def visitConstant_LOCAL_ID(self, ctx:tsqlParser.Constant_LOCAL_IDContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#binary_operator_expression.
    def visitBinary_operator_expression(self, ctx:tsqlParser.Binary_operator_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#percentile_cont_expression.
    def visitPercentile_cont_expression(self, ctx:tsqlParser.Percentile_cont_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#primitive_expression.
    def visitPrimitive_expression(self, ctx:tsqlParser.Primitive_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#bracket_expression.
    def visitBracket_expression(self, ctx:tsqlParser.Bracket_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#unary_operator_expression.
    def visitUnary_operator_expression(self, ctx:tsqlParser.Unary_operator_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#function_call_expression.
    def visitFunction_call_expression(self, ctx:tsqlParser.Function_call_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#conversion_expression.
    def visitConversion_expression(self, ctx:tsqlParser.Conversion_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#case_expression.
    def visitCase_expression(self, ctx:tsqlParser.Case_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_ref_expression.
    def visitColumn_ref_expression(self, ctx:tsqlParser.Column_ref_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#subquery_expression.
    def visitSubquery_expression(self, ctx:tsqlParser.Subquery_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#over_clause_expression.
    def visitOver_clause_expression(self, ctx:tsqlParser.Over_clause_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#constant_expression.
    def visitConstant_expression(self, ctx:tsqlParser.Constant_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#subquery.
    def visitSubquery(self, ctx:tsqlParser.SubqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#with_expression.
    def visitWith_expression(self, ctx:tsqlParser.With_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#common_table_expression.
    def visitCommon_table_expression(self, ctx:tsqlParser.Common_table_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#update_elem.
    def visitUpdate_elem(self, ctx:tsqlParser.Update_elemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#search_condition_list.
    def visitSearch_condition_list(self, ctx:tsqlParser.Search_condition_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#search_cond_or.
    def visitSearch_cond_or(self, ctx:tsqlParser.Search_cond_orContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#search_cond_pred.
    def visitSearch_cond_pred(self, ctx:tsqlParser.Search_cond_predContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#search_cond_and.
    def visitSearch_cond_and(self, ctx:tsqlParser.Search_cond_andContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#unary_operator_expression3.
    def visitUnary_operator_expression3(self, ctx:tsqlParser.Unary_operator_expression3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#unary_operator_expression2.
    def visitUnary_operator_expression2(self, ctx:tsqlParser.Unary_operator_expression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#binary_operator_expression2.
    def visitBinary_operator_expression2(self, ctx:tsqlParser.Binary_operator_expression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sublink_expression.
    def visitSublink_expression(self, ctx:tsqlParser.Sublink_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#binary_mod_expression.
    def visitBinary_mod_expression(self, ctx:tsqlParser.Binary_mod_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#binary_in_expression.
    def visitBinary_in_expression(self, ctx:tsqlParser.Binary_in_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#bracket_search_expression.
    def visitBracket_search_expression(self, ctx:tsqlParser.Bracket_search_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#decimal_expression.
    def visitDecimal_expression(self, ctx:tsqlParser.Decimal_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#bracket_query_expression.
    def visitBracket_query_expression(self, ctx:tsqlParser.Bracket_query_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#query_specification_expression.
    def visitQuery_specification_expression(self, ctx:tsqlParser.Query_specification_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#union_query_expression.
    def visitUnion_query_expression(self, ctx:tsqlParser.Union_query_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#union_op.
    def visitUnion_op(self, ctx:tsqlParser.Union_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#query_specification.
    def visitQuery_specification(self, ctx:tsqlParser.Query_specificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#group_by_grouping_sets.
    def visitGroup_by_grouping_sets(self, ctx:tsqlParser.Group_by_grouping_setsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#grouping_set.
    def visitGrouping_set(self, ctx:tsqlParser.Grouping_setContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#top_clause.
    def visitTop_clause(self, ctx:tsqlParser.Top_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#top_clause_dm.
    def visitTop_clause_dm(self, ctx:tsqlParser.Top_clause_dmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#order_by_clause.
    def visitOrder_by_clause(self, ctx:tsqlParser.Order_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#fetch_expression.
    def visitFetch_expression(self, ctx:tsqlParser.Fetch_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#for_clause.
    def visitFor_clause(self, ctx:tsqlParser.For_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#xml_common_directives.
    def visitXml_common_directives(self, ctx:tsqlParser.Xml_common_directivesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#order_by_expression.
    def visitOrder_by_expression(self, ctx:tsqlParser.Order_by_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#group_by_item.
    def visitGroup_by_item(self, ctx:tsqlParser.Group_by_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#option_clause.
    def visitOption_clause(self, ctx:tsqlParser.Option_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#option.
    def visitOption(self, ctx:tsqlParser.OptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#optimize_for_arg.
    def visitOptimize_for_arg(self, ctx:tsqlParser.Optimize_for_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#select_list.
    def visitSelect_list(self, ctx:tsqlParser.Select_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#select_list_elem.
    def visitSelect_list_elem(self, ctx:tsqlParser.Select_list_elemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_sources.
    def visitTable_sources(self, ctx:tsqlParser.Table_sourcesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#cross_join.
    def visitCross_join(self, ctx:tsqlParser.Cross_joinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_source_item_join.
    def visitTable_source_item_join(self, ctx:tsqlParser.Table_source_item_joinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#standard_join.
    def visitStandard_join(self, ctx:tsqlParser.Standard_joinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#apply_join.
    def visitApply_join(self, ctx:tsqlParser.Apply_joinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#bracket_table_source.
    def visitBracket_table_source(self, ctx:tsqlParser.Bracket_table_sourceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_source_item_name.
    def visitTable_source_item_name(self, ctx:tsqlParser.Table_source_item_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_source_item_simple.
    def visitTable_source_item_simple(self, ctx:tsqlParser.Table_source_item_simpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_source_item_complex.
    def visitTable_source_item_complex(self, ctx:tsqlParser.Table_source_item_complexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#tablesample_clause.
    def visitTablesample_clause(self, ctx:tsqlParser.Tablesample_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sample_number.
    def visitSample_number(self, ctx:tsqlParser.Sample_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#repeat_seed.
    def visitRepeat_seed(self, ctx:tsqlParser.Repeat_seedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_alias.
    def visitTable_alias(self, ctx:tsqlParser.Table_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#change_table.
    def visitChange_table(self, ctx:tsqlParser.Change_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#join_type.
    def visitJoin_type(self, ctx:tsqlParser.Join_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_name_with_hint.
    def visitTable_name_with_hint(self, ctx:tsqlParser.Table_name_with_hintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#rowset_function.
    def visitRowset_function(self, ctx:tsqlParser.Rowset_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#bulk_option.
    def visitBulk_option(self, ctx:tsqlParser.Bulk_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#derived_table.
    def visitDerived_table(self, ctx:tsqlParser.Derived_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#rank_call.
    def visitRank_call(self, ctx:tsqlParser.Rank_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#aggregate_call.
    def visitAggregate_call(self, ctx:tsqlParser.Aggregate_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#standard_call.
    def visitStandard_call(self, ctx:tsqlParser.Standard_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#nvf_call.
    def visitNvf_call(self, ctx:tsqlParser.Nvf_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#cast_call.
    def visitCast_call(self, ctx:tsqlParser.Cast_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#simple_call.
    def visitSimple_call(self, ctx:tsqlParser.Simple_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#expression_call.
    def visitExpression_call(self, ctx:tsqlParser.Expression_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#switch_section.
    def visitSwitch_section(self, ctx:tsqlParser.Switch_sectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#switch_search_condition_section.
    def visitSwitch_search_condition_section(self, ctx:tsqlParser.Switch_search_condition_sectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#with_table_hints.
    def visitWith_table_hints(self, ctx:tsqlParser.With_table_hintsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#insert_with_table_hints.
    def visitInsert_with_table_hints(self, ctx:tsqlParser.Insert_with_table_hintsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_hint.
    def visitTable_hint(self, ctx:tsqlParser.Table_hintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#index_value.
    def visitIndex_value(self, ctx:tsqlParser.Index_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_alias_list.
    def visitColumn_alias_list(self, ctx:tsqlParser.Column_alias_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_alias.
    def visitColumn_alias(self, ctx:tsqlParser.Column_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#a_star.
    def visitA_star(self, ctx:tsqlParser.A_starContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_value_constructor.
    def visitTable_value_constructor(self, ctx:tsqlParser.Table_value_constructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#expression_list.
    def visitExpression_list(self, ctx:tsqlParser.Expression_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#value_list.
    def visitValue_list(self, ctx:tsqlParser.Value_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#next_value_for.
    def visitNext_value_for(self, ctx:tsqlParser.Next_value_forContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#next_value_for_function.
    def visitNext_value_for_function(self, ctx:tsqlParser.Next_value_for_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#ranking_windowed_function.
    def visitRanking_windowed_function(self, ctx:tsqlParser.Ranking_windowed_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#aggregate_windowed_function.
    def visitAggregate_windowed_function(self, ctx:tsqlParser.Aggregate_windowed_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#all_distinct.
    def visitAll_distinct(self, ctx:tsqlParser.All_distinctContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#over_clause.
    def visitOver_clause(self, ctx:tsqlParser.Over_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#row_or_range_clause.
    def visitRow_or_range_clause(self, ctx:tsqlParser.Row_or_range_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#window_frame_extent.
    def visitWindow_frame_extent(self, ctx:tsqlParser.Window_frame_extentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#window_frame_bound.
    def visitWindow_frame_bound(self, ctx:tsqlParser.Window_frame_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#window_frame_preceding.
    def visitWindow_frame_preceding(self, ctx:tsqlParser.Window_frame_precedingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#window_frame_following.
    def visitWindow_frame_following(self, ctx:tsqlParser.Window_frame_followingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_database_option.
    def visitCreate_database_option(self, ctx:tsqlParser.Create_database_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#database_filestream_option.
    def visitDatabase_filestream_option(self, ctx:tsqlParser.Database_filestream_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#database_file_spec.
    def visitDatabase_file_spec(self, ctx:tsqlParser.Database_file_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#file_group.
    def visitFile_group(self, ctx:tsqlParser.File_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#file_spec.
    def visitFile_spec(self, ctx:tsqlParser.File_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#full_table_name.
    def visitFull_table_name(self, ctx:tsqlParser.Full_table_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#table_name.
    def visitTable_name(self, ctx:tsqlParser.Table_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#simple_name.
    def visitSimple_name(self, ctx:tsqlParser.Simple_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#func_proc_name.
    def visitFunc_proc_name(self, ctx:tsqlParser.Func_proc_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#ddl_object.
    def visitDdl_object(self, ctx:tsqlParser.Ddl_objectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#full_column_name.
    def visitFull_column_name(self, ctx:tsqlParser.Full_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#column_name_list.
    def visitColumn_name_list(self, ctx:tsqlParser.Column_name_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#cursor_name.
    def visitCursor_name(self, ctx:tsqlParser.Cursor_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#on_off.
    def visitOn_off(self, ctx:tsqlParser.On_offContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#clustered.
    def visitClustered(self, ctx:tsqlParser.ClusteredContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#null_notnull.
    def visitNull_notnull(self, ctx:tsqlParser.Null_notnullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#scalar_function_name.
    def visitScalar_function_name(self, ctx:tsqlParser.Scalar_function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#default_value.
    def visitDefault_value(self, ctx:tsqlParser.Default_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#constant.
    def visitConstant(self, ctx:tsqlParser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#sign.
    def visitSign(self, ctx:tsqlParser.SignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#r_id.
    def visitR_id(self, ctx:tsqlParser.R_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#simple_id.
    def visitSimple_id(self, ctx:tsqlParser.Simple_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#comparison_operator.
    def visitComparison_operator(self, ctx:tsqlParser.Comparison_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#assignment_operator.
    def visitAssignment_operator(self, ctx:tsqlParser.Assignment_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#file_size.
    def visitFile_size(self, ctx:tsqlParser.File_sizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_or_alter_procedure.
    def visitCreate_or_alter_procedure(self, ctx:tsqlParser.Create_or_alter_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#create_or_alter_function.
    def visitCreate_or_alter_function(self, ctx:tsqlParser.Create_or_alter_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#func_body_returns_select.
    def visitFunc_body_returns_select(self, ctx:tsqlParser.Func_body_returns_selectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#func_body_returns_table.
    def visitFunc_body_returns_table(self, ctx:tsqlParser.Func_body_returns_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#func_body_returns_scalar.
    def visitFunc_body_returns_scalar(self, ctx:tsqlParser.Func_body_returns_scalarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#procedure_param.
    def visitProcedure_param(self, ctx:tsqlParser.Procedure_paramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#procedure_option.
    def visitProcedure_option(self, ctx:tsqlParser.Procedure_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#function_option.
    def visitFunction_option(self, ctx:tsqlParser.Function_optionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#percentile_cont.
    def visitPercentile_cont(self, ctx:tsqlParser.Percentile_contContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by tsqlParser#data_type.
    def visitData_type(self, ctx:tsqlParser.Data_typeContext):
        return self.visitChildren(ctx)



del tsqlParser