"""
Grid model - Represents the 4x4 grid of image cells.
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple


@dataclass
class Grid:
    """
    Represents a 4x4 grid of image cells.
    Each cell can be revealed or masked.
    
    Attributes:
        size: Grid dimension (default 4x4 = 16 cells)
        revealed_cells: Set of revealed cell indices (0-15)
    """
    
    size: int = 4
    revealed_cells: Set[int] = field(default_factory=set)
    
    def __post_init__(self) -> None:
        """Validate grid data."""
        if self.size < 2 or self.size > 8:
            raise ValueError("Grid size must be between 2 and 8")
        max_cells = self.size * self.size
        if any(idx < 0 or idx >= max_cells for idx in self.revealed_cells):
            raise ValueError(f"Cell index must be 0-{max_cells-1}")
    
    def get_total_cells(self) -> int:
        """Get total number of cells in grid."""
        return self.size * self.size
    
    def get_revealed_count(self) -> int:
        """Get number of revealed cells."""
        return len(self.revealed_cells)
    
    def get_hidden_count(self) -> int:
        """Get number of hidden cells."""
        return self.get_total_cells() - self.get_revealed_count()
    
    def reveal_cell(self, cell_index: int) -> bool:
        """
        Reveal a cell.
        
        Args:
            cell_index: Index of cell (0 to size*size-1)
            
        Returns:
            True if cell was just revealed, False if already revealed
            
        Raises:
            ValueError: If cell_index is invalid
        """
        max_cells = self.get_total_cells()
        if cell_index < 0 or cell_index >= max_cells:
            raise ValueError(f"Cell index must be 0-{max_cells-1}")
        
        if cell_index in self.revealed_cells:
            return False  # Already revealed
        
        self.revealed_cells.add(cell_index)
        return True  # Newly revealed
    
    def is_revealed(self, cell_index: int) -> bool:
        """
        Check if a cell is revealed.
        
        Args:
            cell_index: Index of cell
            
        Returns:
            True if revealed, False otherwise
        """
        return cell_index in self.revealed_cells
    
    def get_revealed_cells_list(self) -> List[int]:
        """Get sorted list of revealed cell indices."""
        return sorted(list(self.revealed_cells))
    
    def reset(self) -> None:
        """Reset all cells to hidden state."""
        self.revealed_cells.clear()
    
    def get_grid_position(self, cell_index: int) -> Tuple[int, int]:
        """
        Convert linear index to (row, col) position.
        
        Args:
            cell_index: Linear index (0 to size*size-1)
            
        Returns:
            (row, col) tuple
        """
        row = cell_index // self.size
        col = cell_index % self.size
        return (row, col)
    
    def get_cell_index(self, row: int, col: int) -> int:
        """
        Convert (row, col) position to linear index.
        
        Args:
            row: Row index (0 to size-1)
            col: Column index (0 to size-1)
            
        Returns:
            Linear index (0 to size*size-1)
        """
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            raise ValueError(f"Position ({row}, {col}) is out of bounds for {self.size}x{self.size} grid")
        return row * self.size + col
    
    def __str__(self) -> str:
        """String representation."""
        return f"Grid({self.size}x{self.size}, revealed={self.get_revealed_count()}/{self.get_total_cells()})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Grid(size={self.size}, revealed_cells={sorted(self.revealed_cells)})"
