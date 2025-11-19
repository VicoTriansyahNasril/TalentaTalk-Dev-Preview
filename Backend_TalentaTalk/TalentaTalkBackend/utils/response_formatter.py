# TalentaTalkBackend/utils/response_formatter.py
from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Optional, Dict, Union

class APIResponse:
    """
    Standardized API Response formatter untuk konsistensi response - FIXED VERSION
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Format success response
        
        Args:
            data: Data yang akan dikembalikan
            message: Pesan sukses
            status_code: HTTP status code
            
        Returns:
            JSONResponse dengan format standar
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    @staticmethod
    def error(
        message: str = "Error occurred",
        errors: Optional[Union[str, list, dict]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ) -> JSONResponse:
        """
        Format error response
        
        Args:
            message: Pesan error utama
            errors: Detail error (optional)
            status_code: HTTP status code
            data: Data tambahan (optional)
            
        Returns:
            JSONResponse dengan format error standar
        """
        response_data = {
            "success": False,
            "message": message,
            "data": data
        }
        
        # Tambahkan errors jika ada
        if errors is not None:
            response_data["errors"] = errors
            
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: Dict[str, Any] = None,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    ) -> JSONResponse:
        """
        Format validation error response
        
        Args:
            message: Pesan validation error
            errors: Detail validation errors
            status_code: HTTP status code
            
        Returns:
            JSONResponse dengan format validation error
        """
        response_data = {
            "success": False,
            "message": message,
            "data": None,
            "validation_errors": errors or {}
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    @staticmethod
    def paginated_success(
        data: list,
        total_records: int,
        page: int,
        limit: int,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Format paginated success response
        
        Args:
            data: List data yang akan dikembalikan
            total_records: Total record di database
            page: Current page (1-based)
            limit: Records per page
            message: Success message
            status_code: HTTP status code
            
        Returns:
            JSONResponse dengan format paginated response
        """
        total_pages = (total_records + limit - 1) // limit  # Ceiling division
        
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "totalRecords": total_records,
                "totalPages": total_pages,
                "currentPage": page,
                "pageSize": limit,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            }
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    @staticmethod
    def schema_validation_error(
        field_errors: Dict[str, str],
        message: str = "Validation gagal"
    ) -> JSONResponse:
        """Format error response untuk schema validation"""
        return APIResponse.validation_error(
            message=message,
            errors=field_errors
        )

    @staticmethod
    def duplicate_error(
        resource: str = "Data",
        message: str = None
    ) -> JSONResponse:
        """Format error response untuk duplicate data"""
        if not message:
            message = f"{resource} sudah ada"
        
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def not_found_error(
        resource: str = "Data",
        message: str = None
    ) -> JSONResponse:
        """Format error response untuk data not found"""
        if not message:
            message = f"{resource} tidak ditemukan"
        
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized_error(
        message: str = "Akses tidak diizinkan"
    ) -> JSONResponse:
        """Format error response untuk unauthorized access"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden_error(
        message: str = "Akses ditolak"
    ) -> JSONResponse:
        """Format error response untuk forbidden access"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def server_error(
        message: str = "Terjadi kesalahan server"
    ) -> JSONResponse:
        """Format error response untuk server errors"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class StandardResponses:
    """Common response patterns - ENHANCED VERSION"""
    
    @staticmethod
    def not_found(resource: str = "Resource") -> JSONResponse:
        return APIResponse.not_found_error(resource)
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> JSONResponse:
        return APIResponse.unauthorized_error(message)
    
    @staticmethod
    def forbidden(message: str = "Access forbidden") -> JSONResponse:
        return APIResponse.forbidden_error(message)
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> JSONResponse:
        return APIResponse.server_error(message)
    
    @staticmethod
    def created(data: Any = None, message: str = "Created successfully") -> JSONResponse:
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def deleted(message: str = "Deleted successfully") -> JSONResponse:
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK
        )
    
    @staticmethod
    def updated(data: Any = None, message: str = "Updated successfully") -> JSONResponse:
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def duplicate_entry(resource: str = "Data") -> JSONResponse:
        return APIResponse.duplicate_error(resource)

    @staticmethod
    def invalid_input(message: str = "Input tidak valid") -> JSONResponse:
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def file_error(message: str = "Error pada file") -> JSONResponse:
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def import_success(
        success_count: int,
        error_count: int,
        errors: list = None
    ) -> JSONResponse:
        return APIResponse.success(
            data={
                "successCount": success_count,
                "errorCount": error_count,
                "errors": errors or []
            },
            message=f"Import selesai: {success_count} berhasil, {error_count} error"
        )

    @staticmethod
    def pagination_success(
        data_key: str,
        items: list,
        pagination_info: dict,
        message: str = "Data berhasil diambil"
    ) -> JSONResponse:
        return APIResponse.success(
            data={
                data_key: items,
                "pagination": pagination_info
            },
            message=message
        )