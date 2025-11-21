- Always respond in Vietnamese.

# FastAPI Boilerplate - AI Coding Agent Instructions

## Architecture Overview

This is a **modern FastAPI boilerplate** following the **file-type organization pattern** for clean separation of concerns. The application uses async-first design with PostgreSQL, Redis caching, and comprehensive CRUD operations via FastCRUD.

### Core Components

- **Models**: SQLAlchemy 2.0 ORM models in `src/app/models/` with async support
- **Schemas**: Pydantic V2 models in `src/app/schemas/` for validation and serialization
- **CRUD**: FastCRUD operations in `src/app/crud/` with consistent patterns
- **API Routes**: Organized in `src/app/api/v1/` with dependency injection
- **Core**: Configuration, database, security, and utilities in `src/app/core/`

## Key Patterns & Conventions

### Database Operations (FastCRUD Pattern)

```python
# Standard CRUD definition
CRUDEntity = FastCRUD[Entity, EntityCreateInternal, EntityUpdate, EntityUpdateInternal, EntityDelete, EntityRead]
crud_entity = CRUDEntity(Entity)

# Usage in endpoints
entity = await crud_entity.get(db=db, id=entity_id, schema_to_select=EntityRead)
entities = await crud_entity.get_multi(db=db, offset=0, limit=10, is_deleted=False)
```

- **Always specify `schema_to_select`** for optimized queries
- **Use async sessions** via `async_get_db()` dependency
- **No SQLAlchemy relationships** - use FastCRUD joins instead
- **Soft deletes** with `is_deleted=False` filtering

### Response Patterns (Generic Wrappers)

```python
# From src/app/schemas/base.py
return SuccessResponse[EntityRead](data=entity)
return PaginatedResponse[EntityRead](data=entities, total=count, page=1, page_size=10)
```

### Authentication Dependencies

```python
# Current user (requires auth)
current_user: Annotated[dict, Depends(get_current_user)]

# Optional user (for rate limiting)
user: dict | None = Depends(get_optional_user)

# Superuser only
superuser: Annotated[dict, Depends(get_current_superuser)]
```

### Application Factory Pattern

```python
# From src/app/main.py
app = create_application(router=router, settings=settings, lifespan=lifespan_with_admin)
```

The `create_application()` function configures middleware, database pools, Redis connections, and documentation based on settings types.

## Development Workflow

### Database Migrations

```bash
# From src/ directory
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

### Running the Application

```bash
# Development (from project root)
uv run uvicorn src.app.main:app --reload

# Docker development
docker compose up

# Background worker
uv run arq src.app.core.worker.settings.WorkerSettings
```

### Adding New Models

1. Create model in `src/app/models/entity.py` inheriting from `Base`
2. Create schemas in `src/app/schemas/entity.py` (Base, Create, Read, Update, Delete variants)
3. Create CRUD in `src/app/crud/crud_entity.py` using FastCRUD generic
4. Add to `src/app/models/__init__.py` for migration detection
5. Generate migration with alembic
6. Create API routes in `src/app/api/v1/entity.py`
7. Register router in `src/app/api/v1/__init__.py`

## Critical Configuration Points

### Settings Architecture

Settings classes inherit from specific feature mixins:

- `AppSettings` - Basic app metadata
- `PostgresSettings` - Database configuration
- `RedisCacheSettings` - Redis caching
- `ClientSideCacheSettings` - HTTP caching middleware
- `CRUDAdminSettings` - Admin panel configuration

Remove unused settings from the final `Settings` class to opt out of features.

### Environment-based API Documentation

- **local**: `/docs` and `/redoc` available publicly
- **staging**: Documentation requires superuser authentication
- **production**: Documentation completely disabled

### Rate Limiting with Tiers

Users have `tier_id` linking to rate limits defined per API path. Use `rate_limiter_dependency` for endpoints requiring rate limiting.

## Integration Points

### Admin Panel (CRUDAdmin)

Mounted at `/admin` with models registered in `src/app/admin/views.py`. Supports password hashing, field exclusion, and different session backends.

### Caching (@cache decorator)

```python
@cache(key_prefix="entity_data", resource_id_name="entity_id", expiration=3600)
async def get_entity(request: Request, entity_id: int): ...
```

### Background Tasks (ARQ)

Functions in `src/app/core/worker/functions.py` are automatically queued via Redis.

## Common Gotchas

- **Always import new models** in `src/app/models/__init__.py` for alembic detection
- **Use `schema_to_select`** in CRUD operations to avoid loading unnecessary fields
- **No direct SQLAlchemy relationships** - use FastCRUD's join methods instead
- **Rate limiting requires tiers** - users without tiers use default limits
- **Client middleware only added** if `ClientSideCacheSettings` is in main Settings class
- **Admin initialization happens** in custom lifespan manager with database setup


## 1) Quy tắc chính
- Khi người dùng yêu cầu “phương án”, CHỈ đưa ra các phương án (liệt kê, mô tả ngắn, ưu/nhược điểm, mức rủi ro).
- KHÔNG thực hiện hành động hay thay đổi code ngay lập tức.
- LUÔN yêu cầu người dùng chọn rõ một phương án trước khi triển khai.

## 2) Mẫu cấu trúc trả lời
Phương án <số> — <Tên ngắn>
- Mô tả: <1–2 câu>
- Ưu điểm: <gạch đầu dòng ngắn>
- Nhược điểm: <gạch đầu dòng ngắn>
- Mức độ phức tạp / Rủi ro: <Cao | Trung bình | Thấp>

(…lặp lại cho Phương án 2, 3, …)

👉 Hỏi người dùng:
“Bạn chọn phương án nào? (Ví dụ: 1 hoặc 2)”

## 3) Ví dụ mẫu
Phương án 1 — Tối ưu truy vấn
- Mô tả: Tối ưu SQL và thêm index cho các cột lọc chính.
- Ưu điểm: Dễ triển khai, cải thiện tốc độ đọc.
- Nhược điểm: Không giải quyết được nếu nghẽn do kiến trúc tổng thể.
- Mức độ phức tạp / Rủi ro: Thấp

Phương án 2 — Tách dịch vụ đọc/ghi
- Mô tả: Tách microservice đọc và ghi, dùng replica cho đọc.
- Ưu điểm: Mở rộng tốt, cô lập tải đọc.
- Nhược điểm: Phức tạp hơn, cần thay đổi hạ tầng và deploy.
- Mức độ phức tạp / Rủi ro: Trung bình

👉 “Bạn chọn phương án nào? (Ví dụ: 1 hoặc 2)”

## 4) Lưu ý bắt buộc
- Tuyệt đối KHÔNG tạo file tài liệu (document, README, …) nếu người dùng không yêu cầu.
- Luôn tuân thủ tiêu chí code sạch, chất lượng code, và mọi guideline dành cho AI agent nếu có.