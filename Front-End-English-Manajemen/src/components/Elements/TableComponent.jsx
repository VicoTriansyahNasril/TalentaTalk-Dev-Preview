//src/components/Elements/TableComponent.jsx
import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import {
  Box,
  IconButton,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";

const TableComponent = ({
  columns,
  rows,
  searchValue,
  paginationModel,
  onPaginationModelChange,
  loading,
  getRowId,
  rowCount,
  paginationEnabled = true,
}) => {
  const [filteredRows, setFilteredRows] = useState(rows);

  useEffect(() => {
    if (searchValue) {
      const filtered = rows.filter((row) =>
        columns.some((col) => {
          const cellValue = row[col.field] || "";
          return String(cellValue)
            .toLowerCase()
            .includes(searchValue.toLowerCase());
        })
      );
      setFilteredRows(filtered);
    } else {
      setFilteredRows(rows);
    }
  }, [searchValue, rows, columns]);

  const CustomPaginationComponent = (props) => {
    return (
      <CustomPagination
        paginationModel={paginationModel}
        onPaginationModelChange={onPaginationModelChange}
        rowCount={rowCount}
      />
    );
  };

  return (
    <Box sx={styles.boxTable}>
      <DataGrid
        rows={filteredRows}
        columns={columns}
        paginationMode="server"
        rowCount={rowCount}
        paginationModel={paginationModel}
        onPaginationModelChange={onPaginationModelChange}
        loading={loading}
        autoHeight
        disableRowSelectionOnClick
        disableColumnResize
        disableColumnMenu
        getRowId={getRowId}
        sx={styles.table}
        slots={{
          pagination: paginationEnabled ? CustomPaginationComponent : null,
        }}
      />
    </Box>
  );
};

const CustomPagination = ({
  paginationModel = { pageSize: 10, page: 0 },
  onPaginationModelChange,
  rowCount = 0,
}) => {
  const pageSize = paginationModel?.pageSize || 10;
  const currentPage = paginationModel?.page || 0;
  const totalRows = rowCount || 0;
  
  const pageCount = Math.ceil(totalRows / pageSize) || 1;
  const startRecord = totalRows > 0 ? (currentPage * pageSize + 1) : 0;
  const endRecord = Math.min((currentPage + 1) * pageSize, totalRows);

  const handlePageChange = (newPage) => {
    if (onPaginationModelChange && typeof onPaginationModelChange === 'function') {
      onPaginationModelChange({ ...paginationModel, page: newPage });
    }
  };

  const handlePageSizeChange = (event) => {
    if (onPaginationModelChange && typeof onPaginationModelChange === 'function') {
      onPaginationModelChange({
        ...paginationModel,
        pageSize: parseInt(event.target.value),
        page: 0,
      });
    }
  };

  const renderPageNumbers = () => {
    const pageNumbers = [];
    const maxVisiblePages = 4;

    if (pageCount <= maxVisiblePages) {
      for (let i = 0; i < pageCount; i++) {
        pageNumbers.push(
          <PageNumber
            key={i}
            pageNum={i}
            currentPage={currentPage}
            onClick={() => handlePageChange(i)}
          />
        );
      }
    } else {
      pageNumbers.push(
        <PageNumber
          key={0}
          pageNum={0}
          currentPage={currentPage}
          onClick={() => handlePageChange(0)}
        />
      );

      if (currentPage > 1) {
        pageNumbers.push(<Ellipsis key="ellipsis-start" />);
      }

      const start = Math.max(1, currentPage - 1);
      const end = Math.min(pageCount - 2, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pageNumbers.push(
          <PageNumber
            key={i}
            pageNum={i}
            currentPage={currentPage}
            onClick={() => handlePageChange(i)}
          />
        );
      }

      if (currentPage < pageCount - 2) {
        pageNumbers.push(<Ellipsis key="ellipsis-end" />);
      }

      pageNumbers.push(
        <PageNumber
          key={pageCount - 1}
          pageNum={pageCount - 1}
          currentPage={currentPage}
          onClick={() => handlePageChange(pageCount - 1)}
        />
      );
    }

    return pageNumbers;
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        p: 2,
        width: "100%",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Typography variant="body2" sx={{ mr: 2 }}>
          Showing
        </Typography>
        <Select
          value={pageSize}
          onChange={handlePageSizeChange}
          size="small"
          sx={{ mr: 2, minWidth: 70 }}
        >
          <MenuItem value={10}>10</MenuItem>
          <MenuItem value={25}>25</MenuItem>
          <MenuItem value={50}>50</MenuItem>
        </Select>
      </Box>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Typography variant="body2">
          {totalRows > 0 
            ? `Showing ${startRecord} to ${endRecord} of ${totalRows} entries`
            : "No entries found"
          }
        </Typography>
      </Box>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <IconButton
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 0}
          sx={{ mx: 1 }}
        >
          <ChevronLeftIcon />
        </IconButton>
        {renderPageNumbers()}
        <IconButton
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= pageCount - 1}
          sx={{ mx: 1 }}
        >
          <ChevronRightIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

const PageNumber = ({ pageNum, currentPage, onClick }) => (
  <Box
    onClick={onClick}
    sx={{
      width: 30,
      height: 30,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      cursor: "pointer",
      borderRadius: "4px",
      mx: 0.5,
      border: currentPage === pageNum ? "2px solid #1976d2" : "none",
      color: currentPage === pageNum ? "#1976d2" : "inherit",
      "&:hover": {
        backgroundColor: "rgba(25, 118, 210, 0.04)",
      },
    }}
  >
    {pageNum + 1}
  </Box>
);

const Ellipsis = () => (
  <Box
    sx={{
      width: 30,
      height: 30,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      mx: 0.5,
    }}
  >
    ...
  </Box>
);

const styles = {
  boxTable: {
    width: "100%",
    overflowX: "auto",
  },
  table: {
    border: "none",
    minWidth: 900,
  },
};

export default TableComponent;