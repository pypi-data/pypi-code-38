
chainer_to_keras = {
	"/head/conv1/conv": "conv2d_1",
	"/head/conv1/bn": "batch_normalization_1",

	"/head/conv2/conv": "conv2d_2",
	"/head/conv2/bn": "batch_normalization_2",

	"/head/conv3/conv": "conv2d_3",
	"/head/conv3/bn": "batch_normalization_3",

	"/head/conv5/conv": "conv2d_4",
	"/head/conv5/bn": "batch_normalization_4",

	"/head/conv6/conv": "conv2d_5",
	"/head/conv6/bn": "batch_normalization_5",

	"/mixed00/conv1x1/conv": "conv2d_6",
	"/mixed00/conv1x1/bn": "batch_normalization_6",

	"/mixed00/conv5x5_1/conv": "conv2d_7",
	"/mixed00/conv5x5_1/bn": "batch_normalization_7",

	"/mixed00/conv5x5_2/conv": "conv2d_8",
	"/mixed00/conv5x5_2/bn": "batch_normalization_8",

	"/mixed00/conv3x3_1/conv": "conv2d_9",
	"/mixed00/conv3x3_1/bn": "batch_normalization_9",

	"/mixed00/conv3x3_2/conv": "conv2d_10",
	"/mixed00/conv3x3_2/bn": "batch_normalization_10",

	"/mixed00/conv3x3_3/conv": "conv2d_11",
	"/mixed00/conv3x3_3/bn": "batch_normalization_11",

	"/mixed00/pool_conv/conv": "conv2d_12",
	"/mixed00/pool_conv/bn": "batch_normalization_12",


	"/mixed01/conv1x1/conv": "conv2d_13",
	"/mixed01/conv1x1/bn": "batch_normalization_13",

	"/mixed01/conv5x5_1/conv": "conv2d_14",
	"/mixed01/conv5x5_1/bn": "batch_normalization_14",

	"/mixed01/conv5x5_2/conv": "conv2d_15",
	"/mixed01/conv5x5_2/bn": "batch_normalization_15",

	"/mixed01/conv3x3_1/conv": "conv2d_16",
	"/mixed01/conv3x3_1/bn": "batch_normalization_16",

	"/mixed01/conv3x3_2/conv": "conv2d_17",
	"/mixed01/conv3x3_2/bn": "batch_normalization_17",

	"/mixed01/conv3x3_3/conv": "conv2d_18",
	"/mixed01/conv3x3_3/bn": "batch_normalization_18",

	"/mixed01/pool_conv/conv": "conv2d_19",
	"/mixed01/pool_conv/bn": "batch_normalization_19",


	"/mixed02/conv1x1/conv": "conv2d_20",
	"/mixed02/conv1x1/bn": "batch_normalization_20",

	"/mixed02/conv5x5_1/conv": "conv2d_21",
	"/mixed02/conv5x5_1/bn": "batch_normalization_21",

	"/mixed02/conv5x5_2/conv": "conv2d_22",
	"/mixed02/conv5x5_2/bn": "batch_normalization_22",

	"/mixed02/conv3x3_1/conv": "conv2d_23",
	"/mixed02/conv3x3_1/bn": "batch_normalization_23",

	"/mixed02/conv3x3_2/conv": "conv2d_24",
	"/mixed02/conv3x3_2/bn": "batch_normalization_24",

	"/mixed02/conv3x3_3/conv": "conv2d_25",
	"/mixed02/conv3x3_3/bn": "batch_normalization_25",

	"/mixed02/pool_conv/conv": "conv2d_26",
	"/mixed02/pool_conv/bn": "batch_normalization_26",


	"/mixed03/conv3x3/conv": "conv2d_27",
	"/mixed03/conv3x3/bn": "batch_normalization_27",

	"/mixed03/conv3x3_1/conv": "conv2d_28",
	"/mixed03/conv3x3_1/bn": "batch_normalization_28",

	"/mixed03/conv3x3_2/conv": "conv2d_29",
	"/mixed03/conv3x3_2/bn": "batch_normalization_29",

	"/mixed03/conv3x3_3/conv": "conv2d_30",
	"/mixed03/conv3x3_3/bn": "batch_normalization_30",


	"/mixed04/conv1x1/conv": "conv2d_31",
	"/mixed04/conv1x1/bn": "batch_normalization_31",

	"/mixed04/conv7x7_1/conv": "conv2d_32",
	"/mixed04/conv7x7_1/bn": "batch_normalization_32",

	"/mixed04/conv7x7_2/conv": "conv2d_33",
	"/mixed04/conv7x7_2/bn": "batch_normalization_33",

	"/mixed04/conv7x7_3/conv": "conv2d_34",
	"/mixed04/conv7x7_3/bn": "batch_normalization_34",

	"/mixed04/conv7x7x2_1/conv": "conv2d_35",
	"/mixed04/conv7x7x2_1/bn": "batch_normalization_35",

	"/mixed04/conv7x7x2_2/conv": "conv2d_36",
	"/mixed04/conv7x7x2_2/bn": "batch_normalization_36",

	"/mixed04/conv7x7x2_3/conv": "conv2d_37",
	"/mixed04/conv7x7x2_3/bn": "batch_normalization_37",

	"/mixed04/conv7x7x2_4/conv": "conv2d_38",
	"/mixed04/conv7x7x2_4/bn": "batch_normalization_38",

	"/mixed04/conv7x7x2_5/conv": "conv2d_39",
	"/mixed04/conv7x7x2_5/bn": "batch_normalization_39",

	"/mixed04/pool_conv/conv": "conv2d_40",
	"/mixed04/pool_conv/bn": "batch_normalization_40",


	"/mixed05/conv1x1/conv": "conv2d_41",
	"/mixed05/conv1x1/bn": "batch_normalization_41",

	"/mixed05/conv7x7_1/conv": "conv2d_42",
	"/mixed05/conv7x7_1/bn": "batch_normalization_42",

	"/mixed05/conv7x7_2/conv": "conv2d_43",
	"/mixed05/conv7x7_2/bn": "batch_normalization_43",

	"/mixed05/conv7x7_3/conv": "conv2d_44",
	"/mixed05/conv7x7_3/bn": "batch_normalization_44",

	"/mixed05/conv7x7x2_1/conv": "conv2d_45",
	"/mixed05/conv7x7x2_1/bn": "batch_normalization_45",

	"/mixed05/conv7x7x2_2/conv": "conv2d_46",
	"/mixed05/conv7x7x2_2/bn": "batch_normalization_46",

	"/mixed05/conv7x7x2_3/conv": "conv2d_47",
	"/mixed05/conv7x7x2_3/bn": "batch_normalization_47",

	"/mixed05/conv7x7x2_4/conv": "conv2d_48",
	"/mixed05/conv7x7x2_4/bn": "batch_normalization_48",

	"/mixed05/conv7x7x2_5/conv": "conv2d_49",
	"/mixed05/conv7x7x2_5/bn": "batch_normalization_49",

	"/mixed05/pool_conv/conv": "conv2d_50",
	"/mixed05/pool_conv/bn": "batch_normalization_50",


	"/mixed06/conv1x1/conv": "conv2d_51",
	"/mixed06/conv1x1/bn": "batch_normalization_51",

	"/mixed06/conv7x7_1/conv": "conv2d_52",
	"/mixed06/conv7x7_1/bn": "batch_normalization_52",

	"/mixed06/conv7x7_2/conv": "conv2d_53",
	"/mixed06/conv7x7_2/bn": "batch_normalization_53",

	"/mixed06/conv7x7_3/conv": "conv2d_54",
	"/mixed06/conv7x7_3/bn": "batch_normalization_54",

	"/mixed06/conv7x7x2_1/conv": "conv2d_55",
	"/mixed06/conv7x7x2_1/bn": "batch_normalization_55",

	"/mixed06/conv7x7x2_2/conv": "conv2d_56",
	"/mixed06/conv7x7x2_2/bn": "batch_normalization_56",

	"/mixed06/conv7x7x2_3/conv": "conv2d_57",
	"/mixed06/conv7x7x2_3/bn": "batch_normalization_57",

	"/mixed06/conv7x7x2_4/conv": "conv2d_58",
	"/mixed06/conv7x7x2_4/bn": "batch_normalization_58",

	"/mixed06/conv7x7x2_5/conv": "conv2d_59",
	"/mixed06/conv7x7x2_5/bn": "batch_normalization_59",

	"/mixed06/pool_conv/conv": "conv2d_60",
	"/mixed06/pool_conv/bn": "batch_normalization_60",


	"/mixed07/conv1x1/conv": "conv2d_61",
	"/mixed07/conv1x1/bn": "batch_normalization_61",

	"/mixed07/conv7x7_1/conv": "conv2d_62",
	"/mixed07/conv7x7_1/bn": "batch_normalization_62",

	"/mixed07/conv7x7_2/conv": "conv2d_63",
	"/mixed07/conv7x7_2/bn": "batch_normalization_63",

	"/mixed07/conv7x7_3/conv": "conv2d_64",
	"/mixed07/conv7x7_3/bn": "batch_normalization_64",

	"/mixed07/conv7x7x2_1/conv": "conv2d_65",
	"/mixed07/conv7x7x2_1/bn": "batch_normalization_65",

	"/mixed07/conv7x7x2_2/conv": "conv2d_66",
	"/mixed07/conv7x7x2_2/bn": "batch_normalization_66",

	"/mixed07/conv7x7x2_3/conv": "conv2d_67",
	"/mixed07/conv7x7x2_3/bn": "batch_normalization_67",

	"/mixed07/conv7x7x2_4/conv": "conv2d_68",
	"/mixed07/conv7x7x2_4/bn": "batch_normalization_68",

	"/mixed07/conv7x7x2_5/conv": "conv2d_69",
	"/mixed07/conv7x7x2_5/bn": "batch_normalization_69",

	"/mixed07/pool_conv/conv": "conv2d_70",
	"/mixed07/pool_conv/bn": "batch_normalization_70",


	"/mixed08/conv3x3_1/conv": "conv2d_71",
	"/mixed08/conv3x3_1/bn": "batch_normalization_71",

	"/mixed08/conv3x3_2/conv": "conv2d_72",
	"/mixed08/conv3x3_2/bn": "batch_normalization_72",

	"/mixed08/conv7x7_1/conv": "conv2d_73",
	"/mixed08/conv7x7_1/bn": "batch_normalization_73",

	"/mixed08/conv7x7_2/conv": "conv2d_74",
	"/mixed08/conv7x7_2/bn": "batch_normalization_74",

	"/mixed08/conv7x7_3/conv": "conv2d_75",
	"/mixed08/conv7x7_3/bn": "batch_normalization_75",

	"/mixed08/conv7x7_4/conv": "conv2d_76",
	"/mixed08/conv7x7_4/bn": "batch_normalization_76",


	"/mixed09/conv1x1/conv": "conv2d_77",
	"/mixed09/conv1x1/bn": "batch_normalization_77",

	"/mixed09/conv3x3_1/conv": "conv2d_78",
	"/mixed09/conv3x3_1/bn": "batch_normalization_78",

	"/mixed09/conv3x3_2/conv": "conv2d_79",
	"/mixed09/conv3x3_2/bn": "batch_normalization_79",

	"/mixed09/conv3x3_3/conv": "conv2d_80",
	"/mixed09/conv3x3_3/bn": "batch_normalization_80",

	"/mixed09/conv3x3x2_1/conv": "conv2d_81",
	"/mixed09/conv3x3x2_1/bn": "batch_normalization_81",

	"/mixed09/conv3x3x2_2/conv": "conv2d_82",
	"/mixed09/conv3x3x2_2/bn": "batch_normalization_82",

	"/mixed09/conv3x3x2_3/conv": "conv2d_83",
	"/mixed09/conv3x3x2_3/bn": "batch_normalization_83",

	"/mixed09/conv3x3x2_4/conv": "conv2d_84",
	"/mixed09/conv3x3x2_4/bn": "batch_normalization_84",

	"/mixed09/pool_conv/conv": "conv2d_85",
	"/mixed09/pool_conv/bn": "batch_normalization_85",


	"/mixed10/conv1x1/conv": "conv2d_86",
	"/mixed10/conv1x1/bn": "batch_normalization_86",

	"/mixed10/conv3x3_1/conv": "conv2d_87",
	"/mixed10/conv3x3_1/bn": "batch_normalization_87",

	"/mixed10/conv3x3_2/conv": "conv2d_88",
	"/mixed10/conv3x3_2/bn": "batch_normalization_88",

	"/mixed10/conv3x3_3/conv": "conv2d_89",
	"/mixed10/conv3x3_3/bn": "batch_normalization_89",

	"/mixed10/conv3x3x2_1/conv": "conv2d_90",
	"/mixed10/conv3x3x2_1/bn": "batch_normalization_90",

	"/mixed10/conv3x3x2_2/conv": "conv2d_91",
	"/mixed10/conv3x3x2_2/bn": "batch_normalization_91",

	"/mixed10/conv3x3x2_3/conv": "conv2d_92",
	"/mixed10/conv3x3x2_3/bn": "batch_normalization_92",

	"/mixed10/conv3x3x2_4/conv": "conv2d_93",
	"/mixed10/conv3x3x2_4/bn": "batch_normalization_93",

	"/mixed10/pool_conv/conv": "conv2d_94",
	"/mixed10/pool_conv/bn": "batch_normalization_94",

	# "/fc": "predictions",
	"/fc": "prob",

}

chainer_to_tf_ckpt = {
	"/head/conv1/conv": "Conv2d_1a_3x3",
	"/head/conv1/bn": "Conv2d_1a_3x3/BatchNorm",

	"/head/conv2/conv": "Conv2d_2a_3x3",
	"/head/conv2/bn": "Conv2d_2a_3x3/BatchNorm",

	"/head/conv3/conv": "Conv2d_2b_3x3",
	"/head/conv3/bn": "Conv2d_2b_3x3/BatchNorm",

	"/head/conv5/conv": "Conv2d_3b_1x1",
	"/head/conv5/bn": "Conv2d_3b_1x1/BatchNorm",

	"/head/conv6/conv": "Conv2d_4a_3x3",
	"/head/conv6/bn": "Conv2d_4a_3x3/BatchNorm",

	"/mixed00/conv1x1/conv": "Mixed_5b/Branch_0/Conv2d_0a_1x1",
	"/mixed00/conv1x1/bn": "Mixed_5b/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed00/conv5x5_1/conv": "Mixed_5b/Branch_1/Conv2d_0a_1x1",
	"/mixed00/conv5x5_1/bn": "Mixed_5b/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed00/conv5x5_2/conv": "Mixed_5b/Branch_1/Conv2d_0b_5x5",
	"/mixed00/conv5x5_2/bn": "Mixed_5b/Branch_1/Conv2d_0b_5x5/BatchNorm",

	"/mixed00/conv3x3_1/conv": "Mixed_5b/Branch_2/Conv2d_0a_1x1",
	"/mixed00/conv3x3_1/bn": "Mixed_5b/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed00/conv3x3_2/conv": "Mixed_5b/Branch_2/Conv2d_0b_3x3",
	"/mixed00/conv3x3_2/bn": "Mixed_5b/Branch_2/Conv2d_0b_3x3/BatchNorm",

	"/mixed00/conv3x3_3/conv": "Mixed_5b/Branch_2/Conv2d_0c_3x3",
	"/mixed00/conv3x3_3/bn": "Mixed_5b/Branch_2/Conv2d_0c_3x3/BatchNorm",

	"/mixed00/pool_conv/conv": "Mixed_5b/Branch_3/Conv2d_0b_1x1",
	"/mixed00/pool_conv/bn": "Mixed_5b/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed01/conv1x1/conv": "Mixed_5c/Branch_0/Conv2d_0a_1x1",
	"/mixed01/conv1x1/bn": "Mixed_5c/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed01/conv5x5_1/conv": "Mixed_5c/Branch_1/Conv2d_0b_1x1",
	"/mixed01/conv5x5_1/bn": "Mixed_5c/Branch_1/Conv2d_0b_1x1/BatchNorm",

	"/mixed01/conv5x5_2/conv": "Mixed_5c/Branch_1/Conv_1_0c_5x5",
	"/mixed01/conv5x5_2/bn": "Mixed_5c/Branch_1/Conv_1_0c_5x5/BatchNorm",

	"/mixed01/conv3x3_1/conv": "Mixed_5c/Branch_2/Conv2d_0a_1x1",
	"/mixed01/conv3x3_1/bn": "Mixed_5c/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed01/conv3x3_2/conv": "Mixed_5c/Branch_2/Conv2d_0b_3x3",
	"/mixed01/conv3x3_2/bn": "Mixed_5c/Branch_2/Conv2d_0b_3x3/BatchNorm",

	"/mixed01/conv3x3_3/conv": "Mixed_5c/Branch_2/Conv2d_0c_3x3",
	"/mixed01/conv3x3_3/bn": "Mixed_5c/Branch_2/Conv2d_0c_3x3/BatchNorm",

	"/mixed01/pool_conv/conv": "Mixed_5c/Branch_3/Conv2d_0b_1x1",
	"/mixed01/pool_conv/bn": "Mixed_5c/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed02/conv1x1/conv": "Mixed_5d/Branch_0/Conv2d_0a_1x1",
	"/mixed02/conv1x1/bn": "Mixed_5d/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed02/conv5x5_1/conv": "Mixed_5d/Branch_1/Conv2d_0a_1x1",
	"/mixed02/conv5x5_1/bn": "Mixed_5d/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed02/conv5x5_2/conv": "Mixed_5d/Branch_1/Conv2d_0b_5x5",
	"/mixed02/conv5x5_2/bn": "Mixed_5d/Branch_1/Conv2d_0b_5x5/BatchNorm",

	"/mixed02/conv3x3_1/conv": "Mixed_5d/Branch_2/Conv2d_0a_1x1",
	"/mixed02/conv3x3_1/bn": "Mixed_5d/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed02/conv3x3_2/conv": "Mixed_5d/Branch_2/Conv2d_0b_3x3",
	"/mixed02/conv3x3_2/bn": "Mixed_5d/Branch_2/Conv2d_0b_3x3/BatchNorm",

	"/mixed02/conv3x3_3/conv": "Mixed_5d/Branch_2/Conv2d_0c_3x3",
	"/mixed02/conv3x3_3/bn": "Mixed_5d/Branch_2/Conv2d_0c_3x3/BatchNorm",

	"/mixed02/pool_conv/conv": "Mixed_5d/Branch_3/Conv2d_0b_1x1",
	"/mixed02/pool_conv/bn": "Mixed_5d/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed03/conv3x3/conv": "Mixed_6a/Branch_0/Conv2d_1a_1x1",
	"/mixed03/conv3x3/bn": "Mixed_6a/Branch_0/Conv2d_1a_1x1/BatchNorm",

	"/mixed03/conv3x3_1/conv": "Mixed_6a/Branch_1/Conv2d_0a_1x1",
	"/mixed03/conv3x3_1/bn": "Mixed_6a/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed03/conv3x3_2/conv": "Mixed_6a/Branch_1/Conv2d_0b_3x3",
	"/mixed03/conv3x3_2/bn": "Mixed_6a/Branch_1/Conv2d_0b_3x3/BatchNorm",

	"/mixed03/conv3x3_3/conv": "Mixed_6a/Branch_1/Conv2d_1a_1x1",
	"/mixed03/conv3x3_3/bn": "Mixed_6a/Branch_1/Conv2d_1a_1x1/BatchNorm",


	"/mixed04/conv1x1/conv": "Mixed_6b/Branch_0/Conv2d_0a_1x1",
	"/mixed04/conv1x1/bn": "Mixed_6b/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed04/conv7x7_1/conv": "Mixed_6b/Branch_1/Conv2d_0a_1x1",
	"/mixed04/conv7x7_1/bn": "Mixed_6b/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed04/conv7x7_2/conv": "Mixed_6b/Branch_1/Conv2d_0b_1x7",
	"/mixed04/conv7x7_2/bn": "Mixed_6b/Branch_1/Conv2d_0b_1x7/BatchNorm",

	"/mixed04/conv7x7_3/conv": "Mixed_6b/Branch_1/Conv2d_0c_7x1",
	"/mixed04/conv7x7_3/bn": "Mixed_6b/Branch_1/Conv2d_0c_7x1/BatchNorm",

	"/mixed04/conv7x7x2_1/conv": "Mixed_6b/Branch_2/Conv2d_0a_1x1",
	"/mixed04/conv7x7x2_1/bn": "Mixed_6b/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed04/conv7x7x2_2/conv": "Mixed_6b/Branch_2/Conv2d_0b_7x1",
	"/mixed04/conv7x7x2_2/bn": "Mixed_6b/Branch_2/Conv2d_0b_7x1/BatchNorm",

	"/mixed04/conv7x7x2_3/conv": "Mixed_6b/Branch_2/Conv2d_0c_1x7",
	"/mixed04/conv7x7x2_3/bn": "Mixed_6b/Branch_2/Conv2d_0c_1x7/BatchNorm",

	"/mixed04/conv7x7x2_4/conv": "Mixed_6b/Branch_2/Conv2d_0d_7x1",
	"/mixed04/conv7x7x2_4/bn": "Mixed_6b/Branch_2/Conv2d_0d_7x1/BatchNorm",

	"/mixed04/conv7x7x2_5/conv": "Mixed_6b/Branch_2/Conv2d_0e_1x7",
	"/mixed04/conv7x7x2_5/bn": "Mixed_6b/Branch_2/Conv2d_0e_1x7/BatchNorm",

	"/mixed04/pool_conv/conv": "Mixed_6b/Branch_3/Conv2d_0b_1x1",
	"/mixed04/pool_conv/bn": "Mixed_6b/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed05/conv1x1/conv": "Mixed_6c/Branch_0/Conv2d_0a_1x1",
	"/mixed05/conv1x1/bn": "Mixed_6c/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed05/conv7x7_1/conv": "Mixed_6c/Branch_1/Conv2d_0a_1x1",
	"/mixed05/conv7x7_1/bn": "Mixed_6c/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed05/conv7x7_2/conv": "Mixed_6c/Branch_1/Conv2d_0b_1x7",
	"/mixed05/conv7x7_2/bn": "Mixed_6c/Branch_1/Conv2d_0b_1x7/BatchNorm",

	"/mixed05/conv7x7_3/conv": "Mixed_6c/Branch_1/Conv2d_0c_7x1",
	"/mixed05/conv7x7_3/bn": "Mixed_6c/Branch_1/Conv2d_0c_7x1/BatchNorm",

	"/mixed05/conv7x7x2_1/conv": "Mixed_6c/Branch_2/Conv2d_0a_1x1",
	"/mixed05/conv7x7x2_1/bn": "Mixed_6c/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed05/conv7x7x2_2/conv": "Mixed_6c/Branch_2/Conv2d_0b_7x1",
	"/mixed05/conv7x7x2_2/bn": "Mixed_6c/Branch_2/Conv2d_0b_7x1/BatchNorm",

	"/mixed05/conv7x7x2_3/conv": "Mixed_6c/Branch_2/Conv2d_0c_1x7",
	"/mixed05/conv7x7x2_3/bn": "Mixed_6c/Branch_2/Conv2d_0c_1x7/BatchNorm",

	"/mixed05/conv7x7x2_4/conv": "Mixed_6c/Branch_2/Conv2d_0d_7x1",
	"/mixed05/conv7x7x2_4/bn": "Mixed_6c/Branch_2/Conv2d_0d_7x1/BatchNorm",

	"/mixed05/conv7x7x2_5/conv": "Mixed_6c/Branch_2/Conv2d_0e_1x7",
	"/mixed05/conv7x7x2_5/bn": "Mixed_6c/Branch_2/Conv2d_0e_1x7/BatchNorm",

	"/mixed05/pool_conv/conv": "Mixed_6c/Branch_3/Conv2d_0b_1x1",
	"/mixed05/pool_conv/bn": "Mixed_6c/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed06/conv1x1/conv": "Mixed_6d/Branch_0/Conv2d_0a_1x1",
	"/mixed06/conv1x1/bn": "Mixed_6d/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed06/conv7x7_1/conv": "Mixed_6d/Branch_1/Conv2d_0a_1x1",
	"/mixed06/conv7x7_1/bn": "Mixed_6d/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed06/conv7x7_2/conv": "Mixed_6d/Branch_1/Conv2d_0b_1x7",
	"/mixed06/conv7x7_2/bn": "Mixed_6d/Branch_1/Conv2d_0b_1x7/BatchNorm",

	"/mixed06/conv7x7_3/conv": "Mixed_6d/Branch_1/Conv2d_0c_7x1",
	"/mixed06/conv7x7_3/bn": "Mixed_6d/Branch_1/Conv2d_0c_7x1/BatchNorm",

	"/mixed06/conv7x7x2_1/conv": "Mixed_6d/Branch_2/Conv2d_0a_1x1",
	"/mixed06/conv7x7x2_1/bn": "Mixed_6d/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed06/conv7x7x2_2/conv": "Mixed_6d/Branch_2/Conv2d_0b_7x1",
	"/mixed06/conv7x7x2_2/bn": "Mixed_6d/Branch_2/Conv2d_0b_7x1/BatchNorm",

	"/mixed06/conv7x7x2_3/conv": "Mixed_6d/Branch_2/Conv2d_0c_1x7",
	"/mixed06/conv7x7x2_3/bn": "Mixed_6d/Branch_2/Conv2d_0c_1x7/BatchNorm",

	"/mixed06/conv7x7x2_4/conv": "Mixed_6d/Branch_2/Conv2d_0d_7x1",
	"/mixed06/conv7x7x2_4/bn": "Mixed_6d/Branch_2/Conv2d_0d_7x1/BatchNorm",

	"/mixed06/conv7x7x2_5/conv": "Mixed_6d/Branch_2/Conv2d_0e_1x7",
	"/mixed06/conv7x7x2_5/bn": "Mixed_6d/Branch_2/Conv2d_0e_1x7/BatchNorm",

	"/mixed06/pool_conv/conv": "Mixed_6d/Branch_3/Conv2d_0b_1x1",
	"/mixed06/pool_conv/bn": "Mixed_6d/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed07/conv1x1/conv": "Mixed_6e/Branch_0/Conv2d_0a_1x1",
	"/mixed07/conv1x1/bn": "Mixed_6e/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed07/conv7x7_1/conv": "Mixed_6e/Branch_1/Conv2d_0a_1x1",
	"/mixed07/conv7x7_1/bn": "Mixed_6e/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed07/conv7x7_2/conv": "Mixed_6e/Branch_1/Conv2d_0b_1x7",
	"/mixed07/conv7x7_2/bn": "Mixed_6e/Branch_1/Conv2d_0b_1x7/BatchNorm",

	"/mixed07/conv7x7_3/conv": "Mixed_6e/Branch_1/Conv2d_0c_7x1",
	"/mixed07/conv7x7_3/bn": "Mixed_6e/Branch_1/Conv2d_0c_7x1/BatchNorm",

	"/mixed07/conv7x7x2_1/conv": "Mixed_6e/Branch_2/Conv2d_0a_1x1",
	"/mixed07/conv7x7x2_1/bn": "Mixed_6e/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed07/conv7x7x2_2/conv": "Mixed_6e/Branch_2/Conv2d_0b_7x1",
	"/mixed07/conv7x7x2_2/bn": "Mixed_6e/Branch_2/Conv2d_0b_7x1/BatchNorm",

	"/mixed07/conv7x7x2_3/conv": "Mixed_6e/Branch_2/Conv2d_0c_1x7",
	"/mixed07/conv7x7x2_3/bn": "Mixed_6e/Branch_2/Conv2d_0c_1x7/BatchNorm",

	"/mixed07/conv7x7x2_4/conv": "Mixed_6e/Branch_2/Conv2d_0d_7x1",
	"/mixed07/conv7x7x2_4/bn": "Mixed_6e/Branch_2/Conv2d_0d_7x1/BatchNorm",

	"/mixed07/conv7x7x2_5/conv": "Mixed_6e/Branch_2/Conv2d_0e_1x7",
	"/mixed07/conv7x7x2_5/bn": "Mixed_6e/Branch_2/Conv2d_0e_1x7/BatchNorm",

	"/mixed07/pool_conv/conv": "Mixed_6e/Branch_3/Conv2d_0b_1x1",
	"/mixed07/pool_conv/bn": "Mixed_6e/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed08/conv3x3_1/conv": "Mixed_7a/Branch_0/Conv2d_0a_1x1",
	"/mixed08/conv3x3_1/bn": "Mixed_7a/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed08/conv3x3_2/conv": "Mixed_7a/Branch_0/Conv2d_1a_3x3",
	"/mixed08/conv3x3_2/bn": "Mixed_7a/Branch_0/Conv2d_1a_3x3/BatchNorm",

	"/mixed08/conv7x7_1/conv": "Mixed_7a/Branch_1/Conv2d_0a_1x1",
	"/mixed08/conv7x7_1/bn": "Mixed_7a/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed08/conv7x7_2/conv": "Mixed_7a/Branch_1/Conv2d_0b_1x7",
	"/mixed08/conv7x7_2/bn": "Mixed_7a/Branch_1/Conv2d_0b_1x7/BatchNorm",

	"/mixed08/conv7x7_3/conv": "Mixed_7a/Branch_1/Conv2d_0c_7x1",
	"/mixed08/conv7x7_3/bn": "Mixed_7a/Branch_1/Conv2d_0c_7x1/BatchNorm",

	"/mixed08/conv7x7_4/conv": "Mixed_7a/Branch_1/Conv2d_1a_3x3",
	"/mixed08/conv7x7_4/bn": "Mixed_7a/Branch_1/Conv2d_1a_3x3/BatchNorm",


	"/mixed09/conv1x1/conv": "Mixed_7b/Branch_0/Conv2d_0a_1x1",
	"/mixed09/conv1x1/bn": "Mixed_7b/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed09/conv3x3_1/conv": "Mixed_7b/Branch_1/Conv2d_0a_1x1",
	"/mixed09/conv3x3_1/bn": "Mixed_7b/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed09/conv3x3_2/conv": "Mixed_7b/Branch_1/Conv2d_0b_1x3",
	"/mixed09/conv3x3_2/bn": "Mixed_7b/Branch_1/Conv2d_0b_1x3/BatchNorm",

	"/mixed09/conv3x3_3/conv": "Mixed_7b/Branch_1/Conv2d_0b_3x1",
	"/mixed09/conv3x3_3/bn": "Mixed_7b/Branch_1/Conv2d_0b_3x1/BatchNorm",

	"/mixed09/conv3x3x2_1/conv": "Mixed_7b/Branch_2/Conv2d_0a_1x1",
	"/mixed09/conv3x3x2_1/bn": "Mixed_7b/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed09/conv3x3x2_2/conv": "Mixed_7b/Branch_2/Conv2d_0b_3x3",
	"/mixed09/conv3x3x2_2/bn": "Mixed_7b/Branch_2/Conv2d_0b_3x3/BatchNorm",

	"/mixed09/conv3x3x2_3/conv": "Mixed_7b/Branch_2/Conv2d_0c_1x3",
	"/mixed09/conv3x3x2_3/bn": "Mixed_7b/Branch_2/Conv2d_0c_1x3/BatchNorm",

	"/mixed09/conv3x3x2_4/conv": "Mixed_7b/Branch_2/Conv2d_0d_3x1",
	"/mixed09/conv3x3x2_4/bn": "Mixed_7b/Branch_2/Conv2d_0d_3x1/BatchNorm",

	"/mixed09/pool_conv/conv": "Mixed_7b/Branch_3/Conv2d_0b_1x1",
	"/mixed09/pool_conv/bn": "Mixed_7b/Branch_3/Conv2d_0b_1x1/BatchNorm",


	"/mixed10/conv1x1/conv": "Mixed_7c/Branch_0/Conv2d_0a_1x1",
	"/mixed10/conv1x1/bn": "Mixed_7c/Branch_0/Conv2d_0a_1x1/BatchNorm",

	"/mixed10/conv3x3_1/conv": "Mixed_7c/Branch_1/Conv2d_0a_1x1",
	"/mixed10/conv3x3_1/bn": "Mixed_7c/Branch_1/Conv2d_0a_1x1/BatchNorm",

	"/mixed10/conv3x3_2/conv": "Mixed_7c/Branch_1/Conv2d_0b_1x3",
	"/mixed10/conv3x3_2/bn": "Mixed_7c/Branch_1/Conv2d_0b_1x3/BatchNorm",

	"/mixed10/conv3x3_3/conv": "Mixed_7c/Branch_1/Conv2d_0c_3x1",
	"/mixed10/conv3x3_3/bn": "Mixed_7c/Branch_1/Conv2d_0c_3x1/BatchNorm",

	"/mixed10/conv3x3x2_1/conv": "Mixed_7c/Branch_2/Conv2d_0a_1x1",
	"/mixed10/conv3x3x2_1/bn": "Mixed_7c/Branch_2/Conv2d_0a_1x1/BatchNorm",

	"/mixed10/conv3x3x2_2/conv": "Mixed_7c/Branch_2/Conv2d_0b_3x3",
	"/mixed10/conv3x3x2_2/bn": "Mixed_7c/Branch_2/Conv2d_0b_3x3/BatchNorm",

	"/mixed10/conv3x3x2_3/conv": "Mixed_7c/Branch_2/Conv2d_0c_1x3",
	"/mixed10/conv3x3x2_3/bn": "Mixed_7c/Branch_2/Conv2d_0c_1x3/BatchNorm",

	"/mixed10/conv3x3x2_4/conv": "Mixed_7c/Branch_2/Conv2d_0d_3x1",
	"/mixed10/conv3x3x2_4/bn": "Mixed_7c/Branch_2/Conv2d_0d_3x1/BatchNorm",

	"/mixed10/pool_conv/conv": "Mixed_7c/Branch_3/Conv2d_0b_1x1",
	"/mixed10/pool_conv/bn": "Mixed_7c/Branch_3/Conv2d_0b_1x1/BatchNorm",

	# "/fc": "Logits/Conv2d_1c_1x1",

}
