# Generated from antlr_plsql/plsql.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .plsqlParser import plsqlParser
else:
    from plsqlParser import plsqlParser

# This class defines a complete generic visitor for a parse tree produced by plsqlParser.

class plsqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by plsqlParser#swallow_to_semi.
    def visitSwallow_to_semi(self, ctx:plsqlParser.Swallow_to_semiContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#compilation_unit.
    def visitCompilation_unit(self, ctx:plsqlParser.Compilation_unitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sql_script.
    def visitSql_script(self, ctx:plsqlParser.Sql_scriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sql_explain.
    def visitSql_explain(self, ctx:plsqlParser.Sql_explainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#unit_statement.
    def visitUnit_statement(self, ctx:plsqlParser.Unit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#unit_statement_body.
    def visitUnit_statement_body(self, ctx:plsqlParser.Unit_statement_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_index.
    def visitCreate_index(self, ctx:plsqlParser.Create_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cluster_index_clause.
    def visitCluster_index_clause(self, ctx:plsqlParser.Cluster_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cluster_name.
    def visitCluster_name(self, ctx:plsqlParser.Cluster_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_attributes.
    def visitIndex_attributes(self, ctx:plsqlParser.Index_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#tablespace.
    def visitTablespace(self, ctx:plsqlParser.TablespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#key_compression.
    def visitKey_compression(self, ctx:plsqlParser.Key_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sort_or_nosort.
    def visitSort_or_nosort(self, ctx:plsqlParser.Sort_or_nosortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#visible_or_invisible.
    def visitVisible_or_invisible(self, ctx:plsqlParser.Visible_or_invisibleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#parallel_clause.
    def visitParallel_clause(self, ctx:plsqlParser.Parallel_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_index_clause.
    def visitTable_index_clause(self, ctx:plsqlParser.Table_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_expr.
    def visitIndex_expr(self, ctx:plsqlParser.Index_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_properties.
    def visitIndex_properties(self, ctx:plsqlParser.Index_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#global_partitioned_index.
    def visitGlobal_partitioned_index(self, ctx:plsqlParser.Global_partitioned_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_partitioning_clause.
    def visitIndex_partitioning_clause(self, ctx:plsqlParser.Index_partitioning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#partition_name.
    def visitPartition_name(self, ctx:plsqlParser.Partition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#literal.
    def visitLiteral(self, ctx:plsqlParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#string_function.
    def visitString_function(self, ctx:plsqlParser.String_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#expressions.
    def visitExpressions(self, ctx:plsqlParser.ExpressionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#individual_hash_partitions.
    def visitIndividual_hash_partitions(self, ctx:plsqlParser.Individual_hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#partitioning_storage_clause.
    def visitPartitioning_storage_clause(self, ctx:plsqlParser.Partitioning_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_compression.
    def visitTable_compression(self, ctx:plsqlParser.Table_compressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_partitioning_storage.
    def visitLob_partitioning_storage(self, ctx:plsqlParser.Lob_partitioning_storageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_item.
    def visitLob_item(self, ctx:plsqlParser.Lob_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_segname.
    def visitLob_segname(self, ctx:plsqlParser.Lob_segnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#varray_item.
    def visitVarray_item(self, ctx:plsqlParser.Varray_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hash_partitions_by_quantity.
    def visitHash_partitions_by_quantity(self, ctx:plsqlParser.Hash_partitions_by_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hash_partition_quantity.
    def visitHash_partition_quantity(self, ctx:plsqlParser.Hash_partition_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#local_partitioned_index.
    def visitLocal_partitioned_index(self, ctx:plsqlParser.Local_partitioned_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#on_range_partitioned_table.
    def visitOn_range_partitioned_table(self, ctx:plsqlParser.On_range_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#on_list_partitioned_table.
    def visitOn_list_partitioned_table(self, ctx:plsqlParser.On_list_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#on_hash_partitioned_table.
    def visitOn_hash_partitioned_table(self, ctx:plsqlParser.On_hash_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#on_comp_partitioned_table.
    def visitOn_comp_partitioned_table(self, ctx:plsqlParser.On_comp_partitioned_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_subpartition_clause.
    def visitIndex_subpartition_clause(self, ctx:plsqlParser.Index_subpartition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subpartition_name.
    def visitSubpartition_name(self, ctx:plsqlParser.Subpartition_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#domain_index_clause.
    def visitDomain_index_clause(self, ctx:plsqlParser.Domain_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#indextype.
    def visitIndextype(self, ctx:plsqlParser.IndextypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#odci_parameters.
    def visitOdci_parameters(self, ctx:plsqlParser.Odci_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#local_domain_index_clause.
    def visitLocal_domain_index_clause(self, ctx:plsqlParser.Local_domain_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlindex_clause.
    def visitXmlindex_clause(self, ctx:plsqlParser.Xmlindex_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#local_xmlindex_clause.
    def visitLocal_xmlindex_clause(self, ctx:plsqlParser.Local_xmlindex_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#bitmap_join_index_clause.
    def visitBitmap_join_index_clause(self, ctx:plsqlParser.Bitmap_join_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_table.
    def visitCreate_table(self, ctx:plsqlParser.Create_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#relational_table.
    def visitRelational_table(self, ctx:plsqlParser.Relational_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#relational_properties.
    def visitRelational_properties(self, ctx:plsqlParser.Relational_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_definition.
    def visitColumn_definition(self, ctx:plsqlParser.Column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#inline_ref_constraint.
    def visitInline_ref_constraint(self, ctx:plsqlParser.Inline_ref_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#virtual_column_definition.
    def visitVirtual_column_definition(self, ctx:plsqlParser.Virtual_column_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#out_of_line_constraint.
    def visitOut_of_line_constraint(self, ctx:plsqlParser.Out_of_line_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#foreign_key_clause.
    def visitForeign_key_clause(self, ctx:plsqlParser.Foreign_key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#on_delete_clause.
    def visitOn_delete_clause(self, ctx:plsqlParser.On_delete_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#out_of_line_ref_constraint.
    def visitOut_of_line_ref_constraint(self, ctx:plsqlParser.Out_of_line_ref_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#supplemental_logging_props.
    def visitSupplemental_logging_props(self, ctx:plsqlParser.Supplemental_logging_propsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#supplemental_log_grp_clause.
    def visitSupplemental_log_grp_clause(self, ctx:plsqlParser.Supplemental_log_grp_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#log_grp.
    def visitLog_grp(self, ctx:plsqlParser.Log_grpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#supplemental_id_key_clause.
    def visitSupplemental_id_key_clause(self, ctx:plsqlParser.Supplemental_id_key_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#physical_properties.
    def visitPhysical_properties(self, ctx:plsqlParser.Physical_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#deferred_segment_creation.
    def visitDeferred_segment_creation(self, ctx:plsqlParser.Deferred_segment_creationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#segment_attributes_clause.
    def visitSegment_attributes_clause(self, ctx:plsqlParser.Segment_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#physical_attributes_clause.
    def visitPhysical_attributes_clause(self, ctx:plsqlParser.Physical_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#storage_clause.
    def visitStorage_clause(self, ctx:plsqlParser.Storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#size_clause.
    def visitSize_clause(self, ctx:plsqlParser.Size_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#logging_clause.
    def visitLogging_clause(self, ctx:plsqlParser.Logging_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_properties.
    def visitColumn_properties(self, ctx:plsqlParser.Column_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_type_col_properties.
    def visitObject_type_col_properties(self, ctx:plsqlParser.Object_type_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#substitutable_column_clause.
    def visitSubstitutable_column_clause(self, ctx:plsqlParser.Substitutable_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#nested_table_col_properties.
    def visitNested_table_col_properties(self, ctx:plsqlParser.Nested_table_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#nested_item.
    def visitNested_item(self, ctx:plsqlParser.Nested_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_properties.
    def visitObject_properties(self, ctx:plsqlParser.Object_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#inline_constraint.
    def visitInline_constraint(self, ctx:plsqlParser.Inline_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#references_clause.
    def visitReferences_clause(self, ctx:plsqlParser.References_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#paren_column_list.
    def visitParen_column_list(self, ctx:plsqlParser.Paren_column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_list.
    def visitColumn_list(self, ctx:plsqlParser.Column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#check_constraint.
    def visitCheck_constraint(self, ctx:plsqlParser.Check_constraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constraint_state.
    def visitConstraint_state(self, ctx:plsqlParser.Constraint_stateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#using_index_clause.
    def visitUsing_index_clause(self, ctx:plsqlParser.Using_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#varray_col_properties.
    def visitVarray_col_properties(self, ctx:plsqlParser.Varray_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#varray_storage_clause.
    def visitVarray_storage_clause(self, ctx:plsqlParser.Varray_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_storage_parameters.
    def visitLob_storage_parameters(self, ctx:plsqlParser.Lob_storage_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_parameters.
    def visitLob_parameters(self, ctx:plsqlParser.Lob_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_retention_clause.
    def visitLob_retention_clause(self, ctx:plsqlParser.Lob_retention_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_deduplicate_clause.
    def visitLob_deduplicate_clause(self, ctx:plsqlParser.Lob_deduplicate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_compression_clause.
    def visitLob_compression_clause(self, ctx:plsqlParser.Lob_compression_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#encryption_spec.
    def visitEncryption_spec(self, ctx:plsqlParser.Encryption_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lob_storage_clause.
    def visitLob_storage_clause(self, ctx:plsqlParser.Lob_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmltype_column_properties.
    def visitXmltype_column_properties(self, ctx:plsqlParser.Xmltype_column_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmltype_storage.
    def visitXmltype_storage(self, ctx:plsqlParser.Xmltype_storageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlschema_spec.
    def visitXmlschema_spec(self, ctx:plsqlParser.Xmlschema_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#allow_or_disallow.
    def visitAllow_or_disallow(self, ctx:plsqlParser.Allow_or_disallowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_partitioning_clauses.
    def visitTable_partitioning_clauses(self, ctx:plsqlParser.Table_partitioning_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#range_partitions.
    def visitRange_partitions(self, ctx:plsqlParser.Range_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#range_values_clause.
    def visitRange_values_clause(self, ctx:plsqlParser.Range_values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_partition_description.
    def visitTable_partition_description(self, ctx:plsqlParser.Table_partition_descriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#list_partitions.
    def visitList_partitions(self, ctx:plsqlParser.List_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#list_values_clause.
    def visitList_values_clause(self, ctx:plsqlParser.List_values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hash_partitions.
    def visitHash_partitions(self, ctx:plsqlParser.Hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#composite_range_partitions.
    def visitComposite_range_partitions(self, ctx:plsqlParser.Composite_range_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subpartition_by_range.
    def visitSubpartition_by_range(self, ctx:plsqlParser.Subpartition_by_rangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subpartition_by_list.
    def visitSubpartition_by_list(self, ctx:plsqlParser.Subpartition_by_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subpartition_template.
    def visitSubpartition_template(self, ctx:plsqlParser.Subpartition_templateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#range_subpartition_desc.
    def visitRange_subpartition_desc(self, ctx:plsqlParser.Range_subpartition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#list_subpartition_desc.
    def visitList_subpartition_desc(self, ctx:plsqlParser.List_subpartition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#individual_hash_subparts.
    def visitIndividual_hash_subparts(self, ctx:plsqlParser.Individual_hash_subpartsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hash_subpartition_quantity.
    def visitHash_subpartition_quantity(self, ctx:plsqlParser.Hash_subpartition_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subpartition_by_hash.
    def visitSubpartition_by_hash(self, ctx:plsqlParser.Subpartition_by_hashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#range_partition_desc.
    def visitRange_partition_desc(self, ctx:plsqlParser.Range_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hash_subparts_by_quantity.
    def visitHash_subparts_by_quantity(self, ctx:plsqlParser.Hash_subparts_by_quantityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#composite_list_partitions.
    def visitComposite_list_partitions(self, ctx:plsqlParser.Composite_list_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#list_partition_desc.
    def visitList_partition_desc(self, ctx:plsqlParser.List_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#composite_hash_partitions.
    def visitComposite_hash_partitions(self, ctx:plsqlParser.Composite_hash_partitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#reference_partitioning.
    def visitReference_partitioning(self, ctx:plsqlParser.Reference_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#reference_partition_desc.
    def visitReference_partition_desc(self, ctx:plsqlParser.Reference_partition_descContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#system_partitioning.
    def visitSystem_partitioning(self, ctx:plsqlParser.System_partitioningContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#enable_disable_clause.
    def visitEnable_disable_clause(self, ctx:plsqlParser.Enable_disable_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exceptions_clause.
    def visitExceptions_clause(self, ctx:plsqlParser.Exceptions_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#row_movement_clause.
    def visitRow_movement_clause(self, ctx:plsqlParser.Row_movement_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#flashback_archive_clause.
    def visitFlashback_archive_clause(self, ctx:plsqlParser.Flashback_archive_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_table.
    def visitObject_table(self, ctx:plsqlParser.Object_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_table_substitution.
    def visitObject_table_substitution(self, ctx:plsqlParser.Object_table_substitutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#oid_clause.
    def visitOid_clause(self, ctx:plsqlParser.Oid_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#oid_index_clause.
    def visitOid_index_clause(self, ctx:plsqlParser.Oid_index_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmltype_table.
    def visitXmltype_table(self, ctx:plsqlParser.Xmltype_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmltype_virtual_columns.
    def visitXmltype_virtual_columns(self, ctx:plsqlParser.Xmltype_virtual_columnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_table.
    def visitDrop_table(self, ctx:plsqlParser.Drop_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_table.
    def visitAlter_table(self, ctx:plsqlParser.Alter_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_table_properties.
    def visitAlter_table_properties(self, ctx:plsqlParser.Alter_table_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_table_properties_1.
    def visitAlter_table_properties_1(self, ctx:plsqlParser.Alter_table_properties_1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#supplemental_table_logging.
    def visitSupplemental_table_logging(self, ctx:plsqlParser.Supplemental_table_loggingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#allocate_extent_clause.
    def visitAllocate_extent_clause(self, ctx:plsqlParser.Allocate_extent_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#deallocate_unused_clause.
    def visitDeallocate_unused_clause(self, ctx:plsqlParser.Deallocate_unused_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#upgrade_table_clause.
    def visitUpgrade_table_clause(self, ctx:plsqlParser.Upgrade_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#records_per_block_clause.
    def visitRecords_per_block_clause(self, ctx:plsqlParser.Records_per_block_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_iot_clauses.
    def visitAlter_iot_clauses(self, ctx:plsqlParser.Alter_iot_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_org_table_clause.
    def visitIndex_org_table_clause(self, ctx:plsqlParser.Index_org_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#mapping_table_clause.
    def visitMapping_table_clause(self, ctx:plsqlParser.Mapping_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_org_overflow_clause.
    def visitIndex_org_overflow_clause(self, ctx:plsqlParser.Index_org_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_overflow_clause.
    def visitAlter_overflow_clause(self, ctx:plsqlParser.Alter_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#add_overflow_clause.
    def visitAdd_overflow_clause(self, ctx:plsqlParser.Add_overflow_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#shrink_clause.
    def visitShrink_clause(self, ctx:plsqlParser.Shrink_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_mapping_table_clause.
    def visitAlter_mapping_table_clause(self, ctx:plsqlParser.Alter_mapping_table_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constraint_clauses.
    def visitConstraint_clauses(self, ctx:plsqlParser.Constraint_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#old_constraint_name.
    def visitOld_constraint_name(self, ctx:plsqlParser.Old_constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#new_constraint_name.
    def visitNew_constraint_name(self, ctx:plsqlParser.New_constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_constraint_clause.
    def visitDrop_constraint_clause(self, ctx:plsqlParser.Drop_constraint_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_primary_key_or_unique_or_generic_clause.
    def visitDrop_primary_key_or_unique_or_generic_clause(self, ctx:plsqlParser.Drop_primary_key_or_unique_or_generic_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_clauses.
    def visitColumn_clauses(self, ctx:plsqlParser.Column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#add_modify_drop_column_clauses.
    def visitAdd_modify_drop_column_clauses(self, ctx:plsqlParser.Add_modify_drop_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#add_column_clause.
    def visitAdd_column_clause(self, ctx:plsqlParser.Add_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_column_clauses.
    def visitModify_column_clauses(self, ctx:plsqlParser.Modify_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_column_clause.
    def visitAlter_column_clause(self, ctx:plsqlParser.Alter_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_col_properties.
    def visitModify_col_properties(self, ctx:plsqlParser.Modify_col_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_col_substitutable.
    def visitModify_col_substitutable(self, ctx:plsqlParser.Modify_col_substitutableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_column_clause.
    def visitDrop_column_clause(self, ctx:plsqlParser.Drop_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#rename_column_clause.
    def visitRename_column_clause(self, ctx:plsqlParser.Rename_column_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#old_column_name.
    def visitOld_column_name(self, ctx:plsqlParser.Old_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#new_column_name.
    def visitNew_column_name(self, ctx:plsqlParser.New_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_collection_retrieval.
    def visitModify_collection_retrieval(self, ctx:plsqlParser.Modify_collection_retrievalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#collection_item.
    def visitCollection_item(self, ctx:plsqlParser.Collection_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_lob_storage_clause.
    def visitModify_lob_storage_clause(self, ctx:plsqlParser.Modify_lob_storage_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modify_lob_parameters.
    def visitModify_lob_parameters(self, ctx:plsqlParser.Modify_lob_parametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_function.
    def visitDrop_function(self, ctx:plsqlParser.Drop_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_function.
    def visitAlter_function(self, ctx:plsqlParser.Alter_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_function_body.
    def visitCreate_function_body(self, ctx:plsqlParser.Create_function_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#parallel_enable_clause.
    def visitParallel_enable_clause(self, ctx:plsqlParser.Parallel_enable_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#partition_by_clause.
    def visitPartition_by_clause(self, ctx:plsqlParser.Partition_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#result_cache_clause.
    def visitResult_cache_clause(self, ctx:plsqlParser.Result_cache_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#relies_on_part.
    def visitRelies_on_part(self, ctx:plsqlParser.Relies_on_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#streaming_clause.
    def visitStreaming_clause(self, ctx:plsqlParser.Streaming_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_package.
    def visitDrop_package(self, ctx:plsqlParser.Drop_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_package.
    def visitAlter_package(self, ctx:plsqlParser.Alter_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_package.
    def visitCreate_package(self, ctx:plsqlParser.Create_packageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#package_body.
    def visitPackage_body(self, ctx:plsqlParser.Package_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#package_spec.
    def visitPackage_spec(self, ctx:plsqlParser.Package_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#package_obj_spec.
    def visitPackage_obj_spec(self, ctx:plsqlParser.Package_obj_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#procedure_spec.
    def visitProcedure_spec(self, ctx:plsqlParser.Procedure_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_spec.
    def visitFunction_spec(self, ctx:plsqlParser.Function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#package_obj_body.
    def visitPackage_obj_body(self, ctx:plsqlParser.Package_obj_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_procedure.
    def visitDrop_procedure(self, ctx:plsqlParser.Drop_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_procedure.
    def visitAlter_procedure(self, ctx:plsqlParser.Alter_procedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_procedure_body.
    def visitCreate_procedure_body(self, ctx:plsqlParser.Create_procedure_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_trigger.
    def visitDrop_trigger(self, ctx:plsqlParser.Drop_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_trigger.
    def visitAlter_trigger(self, ctx:plsqlParser.Alter_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_trigger.
    def visitCreate_trigger(self, ctx:plsqlParser.Create_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#trigger_follows_clause.
    def visitTrigger_follows_clause(self, ctx:plsqlParser.Trigger_follows_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#trigger_when_clause.
    def visitTrigger_when_clause(self, ctx:plsqlParser.Trigger_when_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#simple_dml_trigger.
    def visitSimple_dml_trigger(self, ctx:plsqlParser.Simple_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_each_row.
    def visitFor_each_row(self, ctx:plsqlParser.For_each_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#compound_dml_trigger.
    def visitCompound_dml_trigger(self, ctx:plsqlParser.Compound_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#non_dml_trigger.
    def visitNon_dml_trigger(self, ctx:plsqlParser.Non_dml_triggerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#trigger_body.
    def visitTrigger_body(self, ctx:plsqlParser.Trigger_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#routine_clause.
    def visitRoutine_clause(self, ctx:plsqlParser.Routine_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#compound_trigger_block.
    def visitCompound_trigger_block(self, ctx:plsqlParser.Compound_trigger_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#timing_point_section.
    def visitTiming_point_section(self, ctx:plsqlParser.Timing_point_sectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#non_dml_event.
    def visitNon_dml_event(self, ctx:plsqlParser.Non_dml_eventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dml_event_clause.
    def visitDml_event_clause(self, ctx:plsqlParser.Dml_event_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dml_event_element.
    def visitDml_event_element(self, ctx:plsqlParser.Dml_event_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dml_event_nested_clause.
    def visitDml_event_nested_clause(self, ctx:plsqlParser.Dml_event_nested_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#referencing_clause.
    def visitReferencing_clause(self, ctx:plsqlParser.Referencing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#referencing_element.
    def visitReferencing_element(self, ctx:plsqlParser.Referencing_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_type.
    def visitDrop_type(self, ctx:plsqlParser.Drop_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_type.
    def visitAlter_type(self, ctx:plsqlParser.Alter_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#compile_type_clause.
    def visitCompile_type_clause(self, ctx:plsqlParser.Compile_type_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#replace_type_clause.
    def visitReplace_type_clause(self, ctx:plsqlParser.Replace_type_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_method_spec.
    def visitAlter_method_spec(self, ctx:plsqlParser.Alter_method_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_method_element.
    def visitAlter_method_element(self, ctx:plsqlParser.Alter_method_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_attribute_definition.
    def visitAlter_attribute_definition(self, ctx:plsqlParser.Alter_attribute_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#attribute_definition.
    def visitAttribute_definition(self, ctx:plsqlParser.Attribute_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_collection_clauses.
    def visitAlter_collection_clauses(self, ctx:plsqlParser.Alter_collection_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dependent_handling_clause.
    def visitDependent_handling_clause(self, ctx:plsqlParser.Dependent_handling_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dependent_exceptions_part.
    def visitDependent_exceptions_part(self, ctx:plsqlParser.Dependent_exceptions_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_type.
    def visitCreate_type(self, ctx:plsqlParser.Create_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_definition.
    def visitType_definition(self, ctx:plsqlParser.Type_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_type_def.
    def visitObject_type_def(self, ctx:plsqlParser.Object_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_as_part.
    def visitObject_as_part(self, ctx:plsqlParser.Object_as_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_under_part.
    def visitObject_under_part(self, ctx:plsqlParser.Object_under_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#nested_table_type_def.
    def visitNested_table_type_def(self, ctx:plsqlParser.Nested_table_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sqlj_object_type.
    def visitSqlj_object_type(self, ctx:plsqlParser.Sqlj_object_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_body.
    def visitType_body(self, ctx:plsqlParser.Type_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_body_elements.
    def visitType_body_elements(self, ctx:plsqlParser.Type_body_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#map_order_func_declaration.
    def visitMap_order_func_declaration(self, ctx:plsqlParser.Map_order_func_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subprog_decl_in_type.
    def visitSubprog_decl_in_type(self, ctx:plsqlParser.Subprog_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#proc_decl_in_type.
    def visitProc_decl_in_type(self, ctx:plsqlParser.Proc_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#func_decl_in_type.
    def visitFunc_decl_in_type(self, ctx:plsqlParser.Func_decl_in_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constructor_declaration.
    def visitConstructor_declaration(self, ctx:plsqlParser.Constructor_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#modifier_clause.
    def visitModifier_clause(self, ctx:plsqlParser.Modifier_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#object_member_spec.
    def visitObject_member_spec(self, ctx:plsqlParser.Object_member_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sqlj_object_type_attr.
    def visitSqlj_object_type_attr(self, ctx:plsqlParser.Sqlj_object_type_attrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#element_spec.
    def visitElement_spec(self, ctx:plsqlParser.Element_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#element_spec_options.
    def visitElement_spec_options(self, ctx:plsqlParser.Element_spec_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subprogram_spec.
    def visitSubprogram_spec(self, ctx:plsqlParser.Subprogram_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_procedure_spec.
    def visitType_procedure_spec(self, ctx:plsqlParser.Type_procedure_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_function_spec.
    def visitType_function_spec(self, ctx:plsqlParser.Type_function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constructor_spec.
    def visitConstructor_spec(self, ctx:plsqlParser.Constructor_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#map_order_function_spec.
    def visitMap_order_function_spec(self, ctx:plsqlParser.Map_order_function_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pragma_clause.
    def visitPragma_clause(self, ctx:plsqlParser.Pragma_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pragma_elements.
    def visitPragma_elements(self, ctx:plsqlParser.Pragma_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_elements_parameter.
    def visitType_elements_parameter(self, ctx:plsqlParser.Type_elements_parameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#drop_sequence.
    def visitDrop_sequence(self, ctx:plsqlParser.Drop_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alter_sequence.
    def visitAlter_sequence(self, ctx:plsqlParser.Alter_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#create_sequence.
    def visitCreate_sequence(self, ctx:plsqlParser.Create_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sequence_spec.
    def visitSequence_spec(self, ctx:plsqlParser.Sequence_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sequence_start_clause.
    def visitSequence_start_clause(self, ctx:plsqlParser.Sequence_start_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#invoker_rights_clause.
    def visitInvoker_rights_clause(self, ctx:plsqlParser.Invoker_rights_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#compiler_parameters_clause.
    def visitCompiler_parameters_clause(self, ctx:plsqlParser.Compiler_parameters_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#call_spec.
    def visitCall_spec(self, ctx:plsqlParser.Call_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#java_spec.
    def visitJava_spec(self, ctx:plsqlParser.Java_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#c_spec.
    def visitC_spec(self, ctx:plsqlParser.C_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#c_agent_in_clause.
    def visitC_agent_in_clause(self, ctx:plsqlParser.C_agent_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#c_parameters_clause.
    def visitC_parameters_clause(self, ctx:plsqlParser.C_parameters_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#parameter.
    def visitParameter(self, ctx:plsqlParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#default_value_part.
    def visitDefault_value_part(self, ctx:plsqlParser.Default_value_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#declare_spec.
    def visitDeclare_spec(self, ctx:plsqlParser.Declare_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#variable_declaration.
    def visitVariable_declaration(self, ctx:plsqlParser.Variable_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subtype_declaration.
    def visitSubtype_declaration(self, ctx:plsqlParser.Subtype_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_declaration.
    def visitCursor_declaration(self, ctx:plsqlParser.Cursor_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#parameter_spec.
    def visitParameter_spec(self, ctx:plsqlParser.Parameter_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exception_declaration.
    def visitException_declaration(self, ctx:plsqlParser.Exception_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pragma_declaration.
    def visitPragma_declaration(self, ctx:plsqlParser.Pragma_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#record_declaration.
    def visitRecord_declaration(self, ctx:plsqlParser.Record_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#record_type_dec.
    def visitRecord_type_dec(self, ctx:plsqlParser.Record_type_decContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#field_spec.
    def visitField_spec(self, ctx:plsqlParser.Field_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#record_var_dec.
    def visitRecord_var_dec(self, ctx:plsqlParser.Record_var_decContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_declaration.
    def visitTable_declaration(self, ctx:plsqlParser.Table_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_type_dec.
    def visitTable_type_dec(self, ctx:plsqlParser.Table_type_decContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_indexed_by_part.
    def visitTable_indexed_by_part(self, ctx:plsqlParser.Table_indexed_by_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#varray_type_def.
    def visitVarray_type_def(self, ctx:plsqlParser.Varray_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_var_dec.
    def visitTable_var_dec(self, ctx:plsqlParser.Table_var_decContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#seq_of_statements.
    def visitSeq_of_statements(self, ctx:plsqlParser.Seq_of_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#label_declaration.
    def visitLabel_declaration(self, ctx:plsqlParser.Label_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#statement.
    def visitStatement(self, ctx:plsqlParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#assignment_statement.
    def visitAssignment_statement(self, ctx:plsqlParser.Assignment_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#continue_statement.
    def visitContinue_statement(self, ctx:plsqlParser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exit_statement.
    def visitExit_statement(self, ctx:plsqlParser.Exit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#goto_statement.
    def visitGoto_statement(self, ctx:plsqlParser.Goto_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#if_statement.
    def visitIf_statement(self, ctx:plsqlParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#elsif_part.
    def visitElsif_part(self, ctx:plsqlParser.Elsif_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#else_part.
    def visitElse_part(self, ctx:plsqlParser.Else_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#loop_statement.
    def visitLoop_statement(self, ctx:plsqlParser.Loop_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_loop_param.
    def visitCursor_loop_param(self, ctx:plsqlParser.Cursor_loop_paramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#forall_statement.
    def visitForall_statement(self, ctx:plsqlParser.Forall_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#bounds_clause.
    def visitBounds_clause(self, ctx:plsqlParser.Bounds_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#between_bound.
    def visitBetween_bound(self, ctx:plsqlParser.Between_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lower_bound.
    def visitLower_bound(self, ctx:plsqlParser.Lower_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#upper_bound.
    def visitUpper_bound(self, ctx:plsqlParser.Upper_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#null_statement.
    def visitNull_statement(self, ctx:plsqlParser.Null_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#raise_statement.
    def visitRaise_statement(self, ctx:plsqlParser.Raise_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#return_statement.
    def visitReturn_statement(self, ctx:plsqlParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_call.
    def visitFunction_call(self, ctx:plsqlParser.Function_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#body.
    def visitBody(self, ctx:plsqlParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exception_handler.
    def visitException_handler(self, ctx:plsqlParser.Exception_handlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#trigger_block.
    def visitTrigger_block(self, ctx:plsqlParser.Trigger_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#block.
    def visitBlock(self, ctx:plsqlParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sql_statement.
    def visitSql_statement(self, ctx:plsqlParser.Sql_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#execute_immediate.
    def visitExecute_immediate(self, ctx:plsqlParser.Execute_immediateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dynamic_returning_clause.
    def visitDynamic_returning_clause(self, ctx:plsqlParser.Dynamic_returning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#data_manipulation_language_statements.
    def visitData_manipulation_language_statements(self, ctx:plsqlParser.Data_manipulation_language_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_manipulation_statements.
    def visitCursor_manipulation_statements(self, ctx:plsqlParser.Cursor_manipulation_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#close_statement.
    def visitClose_statement(self, ctx:plsqlParser.Close_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#open_statement.
    def visitOpen_statement(self, ctx:plsqlParser.Open_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#fetch_statement.
    def visitFetch_statement(self, ctx:plsqlParser.Fetch_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#open_for_statement.
    def visitOpen_for_statement(self, ctx:plsqlParser.Open_for_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#transaction_control_statements.
    def visitTransaction_control_statements(self, ctx:plsqlParser.Transaction_control_statementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#set_transaction_command.
    def visitSet_transaction_command(self, ctx:plsqlParser.Set_transaction_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#set_constraint_command.
    def visitSet_constraint_command(self, ctx:plsqlParser.Set_constraint_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#commit_statement.
    def visitCommit_statement(self, ctx:plsqlParser.Commit_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#write_clause.
    def visitWrite_clause(self, ctx:plsqlParser.Write_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#rollback_statement.
    def visitRollback_statement(self, ctx:plsqlParser.Rollback_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#savepoint_statement.
    def visitSavepoint_statement(self, ctx:plsqlParser.Savepoint_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#explain_statement.
    def visitExplain_statement(self, ctx:plsqlParser.Explain_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#select_statement.
    def visitSelect_statement(self, ctx:plsqlParser.Select_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subquery_factoring_clause.
    def visitSubquery_factoring_clause(self, ctx:plsqlParser.Subquery_factoring_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#factoring_element.
    def visitFactoring_element(self, ctx:plsqlParser.Factoring_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#search_clause.
    def visitSearch_clause(self, ctx:plsqlParser.Search_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cycle_clause.
    def visitCycle_clause(self, ctx:plsqlParser.Cycle_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#SubqueryParen.
    def visitSubqueryParen(self, ctx:plsqlParser.SubqueryParenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IgnoreSubquery.
    def visitIgnoreSubquery(self, ctx:plsqlParser.IgnoreSubqueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#SubqueryCompound.
    def visitSubqueryCompound(self, ctx:plsqlParser.SubqueryCompoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subquery_operation_part.
    def visitSubquery_operation_part(self, ctx:plsqlParser.Subquery_operation_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#query_block.
    def visitQuery_block(self, ctx:plsqlParser.Query_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#Star1.
    def visitStar1(self, ctx:plsqlParser.Star1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#StarTable.
    def visitStarTable(self, ctx:plsqlParser.StarTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IgnoreTableview_name.
    def visitIgnoreTableview_name(self, ctx:plsqlParser.IgnoreTableview_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#Alias_expr.
    def visitAlias_expr(self, ctx:plsqlParser.Alias_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#from_clause.
    def visitFrom_clause(self, ctx:plsqlParser.From_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_ref_pivot.
    def visitTable_ref_pivot(self, ctx:plsqlParser.Table_ref_pivotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#JoinExpr.
    def visitJoinExpr(self, ctx:plsqlParser.JoinExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#TableRefSimple.
    def visitTableRefSimple(self, ctx:plsqlParser.TableRefSimpleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#TableRefAux.
    def visitTableRefAux(self, ctx:plsqlParser.TableRefAuxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_ref_aux.
    def visitTable_ref_aux(self, ctx:plsqlParser.Table_ref_auxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#join_clause.
    def visitJoin_clause(self, ctx:plsqlParser.Join_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#join_on_part.
    def visitJoin_on_part(self, ctx:plsqlParser.Join_on_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#join_using_part.
    def visitJoin_using_part(self, ctx:plsqlParser.Join_using_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#join_type.
    def visitJoin_type(self, ctx:plsqlParser.Join_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#query_partition_clause.
    def visitQuery_partition_clause(self, ctx:plsqlParser.Query_partition_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#flashback_query_clause.
    def visitFlashback_query_clause(self, ctx:plsqlParser.Flashback_query_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_clause.
    def visitPivot_clause(self, ctx:plsqlParser.Pivot_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_element.
    def visitPivot_element(self, ctx:plsqlParser.Pivot_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_for_clause.
    def visitPivot_for_clause(self, ctx:plsqlParser.Pivot_for_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_in_clause.
    def visitPivot_in_clause(self, ctx:plsqlParser.Pivot_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_in_clause_element.
    def visitPivot_in_clause_element(self, ctx:plsqlParser.Pivot_in_clause_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#pivot_in_clause_elements.
    def visitPivot_in_clause_elements(self, ctx:plsqlParser.Pivot_in_clause_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#unpivot_clause.
    def visitUnpivot_clause(self, ctx:plsqlParser.Unpivot_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#unpivot_in_clause.
    def visitUnpivot_in_clause(self, ctx:plsqlParser.Unpivot_in_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#unpivot_in_elements.
    def visitUnpivot_in_elements(self, ctx:plsqlParser.Unpivot_in_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#hierarchical_query_clause.
    def visitHierarchical_query_clause(self, ctx:plsqlParser.Hierarchical_query_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#start_part.
    def visitStart_part(self, ctx:plsqlParser.Start_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#group_by_clause.
    def visitGroup_by_clause(self, ctx:plsqlParser.Group_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#group_by_elements.
    def visitGroup_by_elements(self, ctx:plsqlParser.Group_by_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#rollup_cube_clause.
    def visitRollup_cube_clause(self, ctx:plsqlParser.Rollup_cube_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#grouping_sets_clause.
    def visitGrouping_sets_clause(self, ctx:plsqlParser.Grouping_sets_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#grouping_sets_elements.
    def visitGrouping_sets_elements(self, ctx:plsqlParser.Grouping_sets_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#having_clause.
    def visitHaving_clause(self, ctx:plsqlParser.Having_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_clause.
    def visitModel_clause(self, ctx:plsqlParser.Model_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cell_reference_options.
    def visitCell_reference_options(self, ctx:plsqlParser.Cell_reference_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#return_rows_clause.
    def visitReturn_rows_clause(self, ctx:plsqlParser.Return_rows_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#reference_model.
    def visitReference_model(self, ctx:plsqlParser.Reference_modelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#main_model.
    def visitMain_model(self, ctx:plsqlParser.Main_modelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_column_clauses.
    def visitModel_column_clauses(self, ctx:plsqlParser.Model_column_clausesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_column_partition_part.
    def visitModel_column_partition_part(self, ctx:plsqlParser.Model_column_partition_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_column_list.
    def visitModel_column_list(self, ctx:plsqlParser.Model_column_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_column.
    def visitModel_column(self, ctx:plsqlParser.Model_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_rules_clause.
    def visitModel_rules_clause(self, ctx:plsqlParser.Model_rules_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_rules_part.
    def visitModel_rules_part(self, ctx:plsqlParser.Model_rules_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_rules_element.
    def visitModel_rules_element(self, ctx:plsqlParser.Model_rules_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cell_assignment.
    def visitCell_assignment(self, ctx:plsqlParser.Cell_assignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_iterate_clause.
    def visitModel_iterate_clause(self, ctx:plsqlParser.Model_iterate_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#until_part.
    def visitUntil_part(self, ctx:plsqlParser.Until_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#order_by_clause.
    def visitOrder_by_clause(self, ctx:plsqlParser.Order_by_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#order_by_elements.
    def visitOrder_by_elements(self, ctx:plsqlParser.Order_by_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_update_clause.
    def visitFor_update_clause(self, ctx:plsqlParser.For_update_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_update_of_part.
    def visitFor_update_of_part(self, ctx:plsqlParser.For_update_of_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_update_options.
    def visitFor_update_options(self, ctx:plsqlParser.For_update_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#limit_clause.
    def visitLimit_clause(self, ctx:plsqlParser.Limit_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#update_statement.
    def visitUpdate_statement(self, ctx:plsqlParser.Update_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#update_set_clause.
    def visitUpdate_set_clause(self, ctx:plsqlParser.Update_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_based_update_set_clause.
    def visitColumn_based_update_set_clause(self, ctx:plsqlParser.Column_based_update_set_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#delete_statement.
    def visitDelete_statement(self, ctx:plsqlParser.Delete_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#insert_statement.
    def visitInsert_statement(self, ctx:plsqlParser.Insert_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#single_table_insert.
    def visitSingle_table_insert(self, ctx:plsqlParser.Single_table_insertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#multi_table_insert.
    def visitMulti_table_insert(self, ctx:plsqlParser.Multi_table_insertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#multi_table_element.
    def visitMulti_table_element(self, ctx:plsqlParser.Multi_table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#conditional_insert_clause.
    def visitConditional_insert_clause(self, ctx:plsqlParser.Conditional_insert_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#conditional_insert_when_part.
    def visitConditional_insert_when_part(self, ctx:plsqlParser.Conditional_insert_when_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#conditional_insert_else_part.
    def visitConditional_insert_else_part(self, ctx:plsqlParser.Conditional_insert_else_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#insert_into_clause.
    def visitInsert_into_clause(self, ctx:plsqlParser.Insert_into_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#values_clause.
    def visitValues_clause(self, ctx:plsqlParser.Values_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#merge_statement.
    def visitMerge_statement(self, ctx:plsqlParser.Merge_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#merge_update_clause.
    def visitMerge_update_clause(self, ctx:plsqlParser.Merge_update_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#merge_element.
    def visitMerge_element(self, ctx:plsqlParser.Merge_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#merge_update_delete_part.
    def visitMerge_update_delete_part(self, ctx:plsqlParser.Merge_update_delete_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#merge_insert_clause.
    def visitMerge_insert_clause(self, ctx:plsqlParser.Merge_insert_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#selected_tableview.
    def visitSelected_tableview(self, ctx:plsqlParser.Selected_tableviewContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lock_table_statement.
    def visitLock_table_statement(self, ctx:plsqlParser.Lock_table_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#wait_nowait_part.
    def visitWait_nowait_part(self, ctx:plsqlParser.Wait_nowait_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lock_table_element.
    def visitLock_table_element(self, ctx:plsqlParser.Lock_table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#lock_mode.
    def visitLock_mode(self, ctx:plsqlParser.Lock_modeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#general_table_ref.
    def visitGeneral_table_ref(self, ctx:plsqlParser.General_table_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#static_returning_clause.
    def visitStatic_returning_clause(self, ctx:plsqlParser.Static_returning_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#error_logging_clause.
    def visitError_logging_clause(self, ctx:plsqlParser.Error_logging_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#error_logging_into_part.
    def visitError_logging_into_part(self, ctx:plsqlParser.Error_logging_into_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#error_logging_reject_part.
    def visitError_logging_reject_part(self, ctx:plsqlParser.Error_logging_reject_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dml_table_expression_clause.
    def visitDml_table_expression_clause(self, ctx:plsqlParser.Dml_table_expression_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_collection_expression.
    def visitTable_collection_expression(self, ctx:plsqlParser.Table_collection_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#subquery_restriction_clause.
    def visitSubquery_restriction_clause(self, ctx:plsqlParser.Subquery_restriction_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sample_clause.
    def visitSample_clause(self, ctx:plsqlParser.Sample_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#seed_part.
    def visitSeed_part(self, ctx:plsqlParser.Seed_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_expression.
    def visitCursor_expression(self, ctx:plsqlParser.Cursor_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#expression_list.
    def visitExpression_list(self, ctx:plsqlParser.Expression_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#condition.
    def visitCondition(self, ctx:plsqlParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IgnoreExpr.
    def visitIgnoreExpr(self, ctx:plsqlParser.IgnoreExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#AndExpr.
    def visitAndExpr(self, ctx:plsqlParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#LikeExpr.
    def visitLikeExpr(self, ctx:plsqlParser.LikeExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#RelExpr.
    def visitRelExpr(self, ctx:plsqlParser.RelExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#MemberExpr.
    def visitMemberExpr(self, ctx:plsqlParser.MemberExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#BetweenExpr.
    def visitBetweenExpr(self, ctx:plsqlParser.BetweenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#CursorExpr.
    def visitCursorExpr(self, ctx:plsqlParser.CursorExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IsExpr.
    def visitIsExpr(self, ctx:plsqlParser.IsExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#NotExpr.
    def visitNotExpr(self, ctx:plsqlParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#InExpr.
    def visitInExpr(self, ctx:plsqlParser.InExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#ParenExpr.
    def visitParenExpr(self, ctx:plsqlParser.ParenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#OrExpr.
    def visitOrExpr(self, ctx:plsqlParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#is_part.
    def visitIs_part(self, ctx:plsqlParser.Is_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_part.
    def visitCursor_part(self, ctx:plsqlParser.Cursor_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#multiset_type.
    def visitMultiset_type(self, ctx:plsqlParser.Multiset_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#relational_operator.
    def visitRelational_operator(self, ctx:plsqlParser.Relational_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#like_type.
    def visitLike_type(self, ctx:plsqlParser.Like_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#like_escape_part.
    def visitLike_escape_part(self, ctx:plsqlParser.Like_escape_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#between_elements.
    def visitBetween_elements(self, ctx:plsqlParser.Between_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#concatenation.
    def visitConcatenation(self, ctx:plsqlParser.ConcatenationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#BinaryExpr.
    def visitBinaryExpr(self, ctx:plsqlParser.BinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IgnoreBinaryExpr.
    def visitIgnoreBinaryExpr(self, ctx:plsqlParser.IgnoreBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#ParenBinaryExpr.
    def visitParenBinaryExpr(self, ctx:plsqlParser.ParenBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#interval_expression.
    def visitInterval_expression(self, ctx:plsqlParser.Interval_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_expression.
    def visitModel_expression(self, ctx:plsqlParser.Model_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#model_expression_element.
    def visitModel_expression_element(self, ctx:plsqlParser.Model_expression_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#single_column_for_loop.
    def visitSingle_column_for_loop(self, ctx:plsqlParser.Single_column_for_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_like_part.
    def visitFor_like_part(self, ctx:plsqlParser.For_like_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#for_increment_decrement_type.
    def visitFor_increment_decrement_type(self, ctx:plsqlParser.For_increment_decrement_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#multi_column_for_loop.
    def visitMulti_column_for_loop(self, ctx:plsqlParser.Multi_column_for_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#IgnoreUnaryExpr.
    def visitIgnoreUnaryExpr(self, ctx:plsqlParser.IgnoreUnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#UnaryExpr.
    def visitUnaryExpr(self, ctx:plsqlParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#case_statement.
    def visitCase_statement(self, ctx:plsqlParser.Case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#simple_case_statement.
    def visitSimple_case_statement(self, ctx:plsqlParser.Simple_case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#simple_case_when_part.
    def visitSimple_case_when_part(self, ctx:plsqlParser.Simple_case_when_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#searched_case_statement.
    def visitSearched_case_statement(self, ctx:plsqlParser.Searched_case_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#searched_case_when_part.
    def visitSearched_case_when_part(self, ctx:plsqlParser.Searched_case_when_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#case_else_part.
    def visitCase_else_part(self, ctx:plsqlParser.Case_else_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#atom.
    def visitAtom(self, ctx:plsqlParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#expression_or_vector.
    def visitExpression_or_vector(self, ctx:plsqlParser.Expression_or_vectorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#vector_expr.
    def visitVector_expr(self, ctx:plsqlParser.Vector_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#quantified_expression.
    def visitQuantified_expression(self, ctx:plsqlParser.Quantified_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#AggregateCall.
    def visitAggregateCall(self, ctx:plsqlParser.AggregateCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#TodoCall.
    def visitTodoCall(self, ctx:plsqlParser.TodoCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#XmlCall.
    def visitXmlCall(self, ctx:plsqlParser.XmlCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#CastCall.
    def visitCastCall(self, ctx:plsqlParser.CastCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#ExtractCall.
    def visitExtractCall(self, ctx:plsqlParser.ExtractCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#WithinOrOverCall.
    def visitWithinOrOverCall(self, ctx:plsqlParser.WithinOrOverCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#aggregate_windowed_function.
    def visitAggregate_windowed_function(self, ctx:plsqlParser.Aggregate_windowed_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#over_clause_keyword.
    def visitOver_clause_keyword(self, ctx:plsqlParser.Over_clause_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#within_or_over_clause_keyword.
    def visitWithin_or_over_clause_keyword(self, ctx:plsqlParser.Within_or_over_clause_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#standard_prediction_function_keyword.
    def visitStandard_prediction_function_keyword(self, ctx:plsqlParser.Standard_prediction_function_keywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#over_clause.
    def visitOver_clause(self, ctx:plsqlParser.Over_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#windowing_clause.
    def visitWindowing_clause(self, ctx:plsqlParser.Windowing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#windowing_type.
    def visitWindowing_type(self, ctx:plsqlParser.Windowing_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#windowing_elements.
    def visitWindowing_elements(self, ctx:plsqlParser.Windowing_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#using_clause.
    def visitUsing_clause(self, ctx:plsqlParser.Using_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#using_element.
    def visitUsing_element(self, ctx:plsqlParser.Using_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#collect_order_by_part.
    def visitCollect_order_by_part(self, ctx:plsqlParser.Collect_order_by_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#within_or_over_part.
    def visitWithin_or_over_part(self, ctx:plsqlParser.Within_or_over_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cost_matrix_clause.
    def visitCost_matrix_clause(self, ctx:plsqlParser.Cost_matrix_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_passing_clause.
    def visitXml_passing_clause(self, ctx:plsqlParser.Xml_passing_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_attributes_clause.
    def visitXml_attributes_clause(self, ctx:plsqlParser.Xml_attributes_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_namespaces_clause.
    def visitXml_namespaces_clause(self, ctx:plsqlParser.Xml_namespaces_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_table_column.
    def visitXml_table_column(self, ctx:plsqlParser.Xml_table_columnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_general_default_part.
    def visitXml_general_default_part(self, ctx:plsqlParser.Xml_general_default_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_multiuse_expression_element.
    def visitXml_multiuse_expression_element(self, ctx:plsqlParser.Xml_multiuse_expression_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlroot_param_version_part.
    def visitXmlroot_param_version_part(self, ctx:plsqlParser.Xmlroot_param_version_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlroot_param_standalone_part.
    def visitXmlroot_param_standalone_part(self, ctx:plsqlParser.Xmlroot_param_standalone_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlserialize_param_enconding_part.
    def visitXmlserialize_param_enconding_part(self, ctx:plsqlParser.Xmlserialize_param_enconding_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlserialize_param_version_part.
    def visitXmlserialize_param_version_part(self, ctx:plsqlParser.Xmlserialize_param_version_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xmlserialize_param_ident_part.
    def visitXmlserialize_param_ident_part(self, ctx:plsqlParser.Xmlserialize_param_ident_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sql_plus_command.
    def visitSql_plus_command(self, ctx:plsqlParser.Sql_plus_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#whenever_command.
    def visitWhenever_command(self, ctx:plsqlParser.Whenever_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#set_command.
    def visitSet_command(self, ctx:plsqlParser.Set_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exit_command.
    def visitExit_command(self, ctx:plsqlParser.Exit_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#prompt_command.
    def visitPrompt_command(self, ctx:plsqlParser.Prompt_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#show_errors_command.
    def visitShow_errors_command(self, ctx:plsqlParser.Show_errors_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#partition_extension_clause.
    def visitPartition_extension_clause(self, ctx:plsqlParser.Partition_extension_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_alias.
    def visitColumn_alias(self, ctx:plsqlParser.Column_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_alias.
    def visitTable_alias(self, ctx:plsqlParser.Table_aliasContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#alias_quoted_string.
    def visitAlias_quoted_string(self, ctx:plsqlParser.Alias_quoted_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#where_clause.
    def visitWhere_clause(self, ctx:plsqlParser.Where_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#current_of_clause.
    def visitCurrent_of_clause(self, ctx:plsqlParser.Current_of_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#into_clause.
    def visitInto_clause(self, ctx:plsqlParser.Into_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#xml_column_name.
    def visitXml_column_name(self, ctx:plsqlParser.Xml_column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cost_class_name.
    def visitCost_class_name(self, ctx:plsqlParser.Cost_class_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#attribute_name.
    def visitAttribute_name(self, ctx:plsqlParser.Attribute_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#savepoint_name.
    def visitSavepoint_name(self, ctx:plsqlParser.Savepoint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#rollback_segment_name.
    def visitRollback_segment_name(self, ctx:plsqlParser.Rollback_segment_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_var_name.
    def visitTable_var_name(self, ctx:plsqlParser.Table_var_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#schema_name.
    def visitSchema_name(self, ctx:plsqlParser.Schema_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#routine_name.
    def visitRoutine_name(self, ctx:plsqlParser.Routine_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#package_name.
    def visitPackage_name(self, ctx:plsqlParser.Package_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#implementation_type_name.
    def visitImplementation_type_name(self, ctx:plsqlParser.Implementation_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#parameter_name.
    def visitParameter_name(self, ctx:plsqlParser.Parameter_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#reference_model_name.
    def visitReference_model_name(self, ctx:plsqlParser.Reference_model_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#main_model_name.
    def visitMain_model_name(self, ctx:plsqlParser.Main_model_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#aggregate_function_name.
    def visitAggregate_function_name(self, ctx:plsqlParser.Aggregate_function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#query_name.
    def visitQuery_name(self, ctx:plsqlParser.Query_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constraint_name.
    def visitConstraint_name(self, ctx:plsqlParser.Constraint_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#label_name.
    def visitLabel_name(self, ctx:plsqlParser.Label_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_name.
    def visitType_name(self, ctx:plsqlParser.Type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#sequence_name.
    def visitSequence_name(self, ctx:plsqlParser.Sequence_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#exception_name.
    def visitException_name(self, ctx:plsqlParser.Exception_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_name.
    def visitFunction_name(self, ctx:plsqlParser.Function_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#procedure_name.
    def visitProcedure_name(self, ctx:plsqlParser.Procedure_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#trigger_name.
    def visitTrigger_name(self, ctx:plsqlParser.Trigger_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#variable_name.
    def visitVariable_name(self, ctx:plsqlParser.Variable_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#index_name.
    def visitIndex_name(self, ctx:plsqlParser.Index_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#cursor_name.
    def visitCursor_name(self, ctx:plsqlParser.Cursor_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#record_name.
    def visitRecord_name(self, ctx:plsqlParser.Record_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#collection_name.
    def visitCollection_name(self, ctx:plsqlParser.Collection_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#link_name.
    def visitLink_name(self, ctx:plsqlParser.Link_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#column_name.
    def visitColumn_name(self, ctx:plsqlParser.Column_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#tableview_name.
    def visitTableview_name(self, ctx:plsqlParser.Tableview_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#dot_id.
    def visitDot_id(self, ctx:plsqlParser.Dot_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#star.
    def visitStar(self, ctx:plsqlParser.StarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#keep_clause.
    def visitKeep_clause(self, ctx:plsqlParser.Keep_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_argument.
    def visitFunction_argument(self, ctx:plsqlParser.Function_argumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_argument_analytic.
    def visitFunction_argument_analytic(self, ctx:plsqlParser.Function_argument_analyticContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#function_argument_modeling.
    def visitFunction_argument_modeling(self, ctx:plsqlParser.Function_argument_modelingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#respect_or_ignore_nulls.
    def visitRespect_or_ignore_nulls(self, ctx:plsqlParser.Respect_or_ignore_nullsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#argument.
    def visitArgument(self, ctx:plsqlParser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#type_spec.
    def visitType_spec(self, ctx:plsqlParser.Type_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#datatype.
    def visitDatatype(self, ctx:plsqlParser.DatatypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#precision_part.
    def visitPrecision_part(self, ctx:plsqlParser.Precision_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#native_datatype_element.
    def visitNative_datatype_element(self, ctx:plsqlParser.Native_datatype_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#bind_variable.
    def visitBind_variable(self, ctx:plsqlParser.Bind_variableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#FuncCall.
    def visitFuncCall(self, ctx:plsqlParser.FuncCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#Identifier.
    def visitIdentifier(self, ctx:plsqlParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#table_element.
    def visitTable_element(self, ctx:plsqlParser.Table_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#constant.
    def visitConstant(self, ctx:plsqlParser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#numeric.
    def visitNumeric(self, ctx:plsqlParser.NumericContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#numeric_negative.
    def visitNumeric_negative(self, ctx:plsqlParser.Numeric_negativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#quoted_string.
    def visitQuoted_string(self, ctx:plsqlParser.Quoted_stringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#r_id.
    def visitR_id(self, ctx:plsqlParser.R_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#id_expression.
    def visitId_expression(self, ctx:plsqlParser.Id_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#not_equal_op.
    def visitNot_equal_op(self, ctx:plsqlParser.Not_equal_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#greater_than_or_equals_op.
    def visitGreater_than_or_equals_op(self, ctx:plsqlParser.Greater_than_or_equals_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#less_than_or_equals_op.
    def visitLess_than_or_equals_op(self, ctx:plsqlParser.Less_than_or_equals_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#concatenation_op.
    def visitConcatenation_op(self, ctx:plsqlParser.Concatenation_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#outer_join_sign.
    def visitOuter_join_sign(self, ctx:plsqlParser.Outer_join_signContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by plsqlParser#regular_id.
    def visitRegular_id(self, ctx:plsqlParser.Regular_idContext):
        return self.visitChildren(ctx)



del plsqlParser