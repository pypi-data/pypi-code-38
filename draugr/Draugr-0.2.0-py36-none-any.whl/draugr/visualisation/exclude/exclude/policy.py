class Policy(Architecture):
  def __init__(self, num_inputs, action_space):
    super().__init__()

  @property
  def state_size(self):
    """
      Size of the recurrent state of the model (propagated between steps)
      """
    return 128

  def forward(self, inputs, states, masks):
    value = 0
    actions = 0
    return value, actions, states
