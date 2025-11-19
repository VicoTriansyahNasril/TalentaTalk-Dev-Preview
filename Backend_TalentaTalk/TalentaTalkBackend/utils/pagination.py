# utils/pagination.py
from typing import Dict, List, Any, Optional

class PaginationHelper:
    """Helper class untuk standardisasi pagination sesuai dokumentasi API"""
    
    ALLOWED_PAGE_SIZES = [10, 25, 50]
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50

    @staticmethod
    def validate_pagination_params(page: int, size: int) -> tuple[int, int]:
        """Validasi parameter pagination dengan format yang tepat"""
        if page < 1:
            page = 1
        
        if size not in PaginationHelper.ALLOWED_PAGE_SIZES:
            size = PaginationHelper.DEFAULT_PAGE_SIZE
        
        return page, size

    @staticmethod
    def calculate_pagination_info(total_items: int, page: int, size: int) -> Dict[str, Any]:
        """Menghitung informasi pagination sesuai format dokumentasi API"""
        if total_items == 0:
            return {
                "currentPage": page,
                "totalPages": 0,
                "totalRecords": 0,
                "showing": "0 records found"
            }
        
        total_pages = (total_items + size - 1) // size
        start_item = ((page - 1) * size) + 1
        end_item = min(page * size, total_items)
        
        return {
            "currentPage": page,
            "totalPages": total_pages,
            "totalRecords": total_items,
            "showing": f"{start_item} to {end_item} out of {total_items} records"
        }

    @staticmethod
    def create_paginated_response(
        data: List[Any], 
        total_items: int, 
        page: int, 
        size: int,
        data_key: str = "data",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Membuat response pagination sesuai format dokumentasi API Web"""
        page, size = PaginationHelper.validate_pagination_params(page, size)
        pagination_info = PaginationHelper.calculate_pagination_info(total_items, page, size)
        
        response_data = {
            data_key: data,
            "pagination": pagination_info
        }
        
        if additional_data:
            response_data.update(additional_data)
            
        return response_data

    @staticmethod 
    def create_api_response_with_pagination(
        data: List[Any],
        total_items: int,
        page: int,
        size: int,
        message: str = "Data retrieved successfully",
        data_key: str = "data",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Membuat complete API response dengan pagination format dokumentasi"""
        paginated_data = PaginationHelper.create_paginated_response(
            data, total_items, page, size, data_key, additional_data
        )
        
        return {
            "data": paginated_data,
            "message": message,
            "statusCode": 200,
            "status": "OK"
        }

    @staticmethod
    def get_offset_limit(page: int, size: int) -> tuple[int, int]:
        """Helper untuk mendapatkan offset dan limit untuk database query"""
        page, size = PaginationHelper.validate_pagination_params(page, size)
        offset = (page - 1) * size
        return offset, size

def paginate_learners_list(
    learners: List[Any],
    total_count: int,
    page: int, 
    size: int,
    category_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Specialized pagination untuk learners list dengan category info"""
    additional_data = {}
    if category_info:
        additional_data["categoryInfo"] = category_info
        
    return PaginationHelper.create_api_response_with_pagination(
        data=learners,
        total_items=total_count,
        page=page,
        size=size,
        message="Data ranking berhasil diambil",
        data_key="learners",
        additional_data=additional_data
    )