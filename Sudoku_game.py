############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import copy

############################################################
# Sudoku Solver
############################################################


def sudoku_cells():
    # returns the list of all cells as (row, column) pairs
    cell_lst = []
    for row in range(9):
        for col in range(9):
            cell_lst.append((row, col))
    return cell_lst


def sudoku_arcs():
    # return list of arcs between cells corresponding to inequality constraints
    arcs = []
    cell_lst = sudoku_cells()

    for cell1 in cell_lst:
        for cell2 in cell_lst:
            # if the cells are different, get row and column index of the cell
            if cell1 != cell2:
                row1, col1 = cell1
                row2, col2 = cell2

                # if 2 cells share same row, column or sub square, add to list
                if row1 == row2 or col1 == col2 or (row1 // 3 == row2 // 3 and
                                                    col1 // 3 == col2 // 3):
                    arcs.append((cell1, cell2))

    return arcs


def read_board(path):
    # reads the board by file at the given path and returns it as a dictionary
    with open(path, 'r') as file:
        lines = file.readlines()

    board = {}
    for row in range(9):
        for col in range(9):
            cell = lines[row][col]
            if cell != '\n':
                # if the current cell is blank, it contains any digit
                if cell != '*':
                    board[(row, col)] = set([int(cell)])
                else:
                    board[(row, col)] = set(range(1, 10))

    return board


class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        # returns the set of values at current particular cell
        return self.board[cell]

    def remove_inconsistent_values(self, cell1, cell2):
        # removes a value in cell1 that does not satisfy
        # inequality constraints in cell2
        if (cell1, cell2) in self.ARCS:
            value_set1 = self.board[cell1]
            value_set2 = self.board[cell2]

            # check if cell 2 already has the value
            if len(value_set2) == 1 and value_set2.issubset(value_set1):
                value_set1 -= value_set2
                return True

        return False

    def infer_ac3(self):
        # initialize queue with the cell pairs
        arcs = self.ARCS
        queue = arcs.copy()

        # iterate queue untill it's empty
        while queue:
            cell1, cell2 = queue.pop(0)
            # if inconsistent values are removed check other arcs
            if self.remove_inconsistent_values(cell1, cell2):
                for new_pair in self.ARCS:
                    if new_pair[1] == cell1:
                        queue.append(new_pair)

    def unique_col_check(self, value, row, col):
        # checks if the value of the current cell is unique in the column
        for r in range(9):
            if r != row and value in self.board[(r, col)]:
                return False
        return True

    def unique_row_check(self, value, row, col):
        # checks if the value of the current cell is unique in the row
        for c in range(9):
            if c != col and value in self.board[(row, c)]:
                return False
        return True

    def unique_square_check(self, value, cell):
        # get row and the column index of the start cell
        row_s = cell[0] // 3
        col_s = cell[1] // 3

        # checks if the value is unique in 3x3 sub square
        for r in range(row_s, row_s + 3):
            for c in range(col_s, col_s + 3):
                if (r != cell[0] or c != cell[1]) and \
                        value in self.board[(cell)]:
                    return False
        return True

    def infer_improved(self):
        additional_infer = True
        while additional_infer:
            self.infer_ac3()
            additional_infer = False

            # iterate each cell
            for cell in self.CELLS:
                if len(self.board[cell]) > 1:

                    # iterate the value of cell and check if it's unique
                    for value in self.board[cell]:
                        row, col = cell
                        if self.unique_col_check(value, row, col) or \
                                self.unique_row_check(value, row, col) or \
                                self.unique_square_check(value, cell):

                            # update the cell to a specific value
                            self.board[cell] = {value}
                            additional_infer = True
                            break

    def is_solved(self):  # iterate each cell and check if problem is solved
        for cell in self.CELLS:
            if len(self.board[cell]) != 1:
                return False
        return True

    def infer_with_guessing(self):
        self.infer_improved()
        for cell in self.CELLS:
            if len(self.board[cell]) > 1:

                # iterate each possible value of the cell
                for value in self.board[cell]:
                    copied_board = copy.deepcopy(self.board)

                    # assigns the current possible value to the cell
                    self.board[cell] = {value}
                    self.infer_with_guessing()

                    # check if the problem is solved, backtrack if needed
                    if self.is_solved():
                        break

                    # go back to the board before guessing
                    self.board = copied_board
                break
