from gherkan.containers.StatementTreeNode import StatementTreeNode, StatementTreeBinaryOperatorNode
from gherkan.decoder.SignalParser import SignalParser


def processNode(node: StatementTreeNode):
    """This function will process a tree node and return a string depending on the node parameters

    Arguments:
        node {SignalStatementTreeNode} -- The tree node

    Returns:
        str -- A string representing the tree node
    """

    # Obviously, the return value will depend on what we want to do with the node
    return node.kind + "; "


def recurseIntoTree(node: StatementTreeNode):
    """This function will recursively traverse the tree deeper and deeper
       until all the nodes are processed with the "processNode" function.

    Arguments:
        node {SignalStatementTreeNode} -- The tree node

    Returns:
        str -- A result string. This can be anything depending on what the process function should return.
    """

    # Apply the function onto this node
    result = processNode(node)

    # If the current node type is "operator", i.e. it has children,
    # traverse deeper into its children
    if type(node) is StatementTreeBinaryOperatorNode:
        # Retrieve result from the left child
        result += recurseIntoTree(node.lchild)
        # and then retrieve result from the right child
        result += recurseIntoTree(node.rchild)

    # Return the result
    return result


if __name__ == "__main__":
    # Parse statement into the SignalStatementTree
    signalParser = SignalParser()
    st = signalParser.parseStatement("part2OnTable == 1 && (robotN1ProgramNumber == 0 || robotN1ProgramNumber == 1 || robotN1ProgramEnded) && edge(robotN3ProgramEnded, 1)")

    # Call the recursive function with the tree's *root* as an argument
    result = recurseIntoTree(st.root)

    # print result
    print(result)
