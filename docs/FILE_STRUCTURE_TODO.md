# File Structure Todo - Based on SDD

## Development Rule
DO NOT USE EMOJIS IN CODE OR DOCUMENTATION

---

## Status Summary
- [DONE] Folder structure created
- [PARTIAL] Backend: 1 file exists (main.py), 80+ files missing
- [PARTIAL] Frontend: 4 files exist (main.tsx, App.tsx, App.css, index.css), 30+ files missing
- [DONE] Documentation: BACKEND_SETUP.md created

---

## Backend Files to Create

### Core Application
- [ ] `backend/__init__.py` - Package initializer
- [ ] `backend/config.py` - Configuration and environment variable management
- [DONE] `backend/main.py` - Already exists (FastAPI entry point)

### API Layer (`backend/api/`)
- [ ] `backend/api/__init__.py`
- [ ] `backend/api/routes.py` - FastAPI route handlers for HTTP endpoints
- [ ] `backend/api/dependencies.py` - Dependency injection for routes
- [ ] `backend/api/middleware.py` - Request/response middleware

### Models (`backend/models/`)
Data validation using Pydantic
- [ ] `backend/models/__init__.py`
- [ ] `backend/models/receipt.py` - Receipt data models
- [ ] `backend/models/item.py` - Receipt item models with financial fields
- [ ] `backend/models/store.py` - Store-related models
- [ ] `backend/models/user.py` - User and account models
- [ ] `backend/models/rebate.py` - Rebate/offer models
- [ ] `backend/models/base.py` - Base models and common types

### Services (`backend/services/`)
Business logic layer (Rule 6: Services call repositories)
- [ ] `backend/services/__init__.py`
- [ ] `backend/services/receipt_service.py` - Receipt processing logic
- [ ] `backend/services/item_service.py` - Item processing logic
- [ ] `backend/services/store_service.py` - Store data management
- [ ] `backend/services/user_service.py` - User management
- [ ] `backend/services/rebate_service.py` - Rebate/offer logic
- [ ] `backend/services/financial_service.py` - Financial aggregation (Rule 3: Keep financial fields separate)

### Database/Repository (`backend/repositories/`)
Data access layer
- [ ] `backend/repositories/__init__.py`
- [ ] `backend/repositories/receipt_repo.py` - MongoDB receipt operations
- [ ] `backend/repositories/item_repo.py` - MongoDB item operations
- [ ] `backend/repositories/base_repo.py` - Base repository pattern with Motor (async MongoDB)

### ETL Pipeline (`backend/etl/`)
Stage-based processing with clear separation (Rule 2)
- [ ] `backend/etl/__init__.py`
- [ ] `backend/etl/extractors.py` - OCR extraction only. No parsing.
- [ ] `backend/etl/loaders.py` - Database writes only. No parsing.
- [ ] `backend/etl/stages.py` - Pipeline orchestration
- [ ] `backend/etl/validators.py` - Data validation between stages

### Parsers (`backend/parsers/`)
Store-specific parsing logic (Rule 1: Store isolation)
- [ ] `backend/parsers/__init__.py`
- [ ] `backend/parsers/base_parser.py` - Abstract base parser
- [ ] `backend/parsers/parser_registry.py` - Factory for store parsers

#### CVS Parser
- [ ] `backend/parsers/cvs/__init__.py`
- [ ] `backend/parsers/cvs/parser.py` - CVS receipt parsing logic
- [ ] `backend/parsers/cvs/rules.py` - CVS-specific business rules

#### HEB Parser
- [ ] `backend/parsers/heb/__init__.py`
- [ ] `backend/parsers/heb/parser.py` - HEB receipt parsing logic
- [ ] `backend/parsers/heb/rules.py` - HEB-specific business rules

#### Walgreens Parser
- [ ] `backend/parsers/walgreens/__init__.py`
- [ ] `backend/parsers/walgreens/parser.py` - Walgreens receipt parsing logic
- [ ] `backend/parsers/walgreens/rules.py` - Walgreens-specific business rules

#### Walmart Parser
- [ ] `backend/parsers/walmart/__init__.py`
- [ ] `backend/parsers/walmart/parser.py` - Walmart receipt parsing logic
- [ ] `backend/parsers/walmart/rules.py` - Walmart-specific business rules

#### Rebate Apps Parser
- [ ] `backend/parsers/rebate_apps/__init__.py`
- [ ] `backend/parsers/rebate_apps/parser.py` - Rebate app receipt parsing
- [ ] `backend/parsers/rebate_apps/rules.py` - Rebate app-specific rules

### Normalizer (`backend/normalizer/`)
Rule-based lookup against normalization rules
- [ ] `backend/normalizer/__init__.py`
- [ ] `backend/normalizer/normalizer.py` - Core normalization engine
- [ ] `backend/normalizer/rules.py` - Normalization rule definitions

### ML (`backend/ml/`)
Machine learning models
- [ ] `backend/ml/__init__.py`
- [ ] `backend/ml/models.py` - Trained TF-IDF/classifier models
- [ ] `backend/ml/item_classifier.py` - Item classification
- [ ] `backend/ml/store_classifier.py` - Store identification

### Tests (`backend/tests/`)
Unit and integration tests
- [ ] `backend/tests/__init__.py`
- [ ] `backend/tests/test_extractors.py` - OCR extraction tests
- [ ] `backend/tests/test_parsers.py` - Parser logic tests
- [ ] `backend/tests/test_services.py` - Service layer tests
- [ ] `backend/tests/test_models.py` - Pydantic model validation
- [ ] `backend/tests/test_api.py` - API endpoint tests
- [ ] `backend/tests/conftest.py` - Pytest fixtures

---

## Frontend Files to Create

### Core (`frontend/src/`)
- [DONE] `frontend/src/main.tsx` - React entry point
- [DONE] `frontend/src/App.tsx` - Main app component
- [DONE] `frontend/src/App.css` - Main app styles
- [DONE] `frontend/src/index.css` - Global styles
- [ ] `frontend/src/vite-env.d.ts` - Vite TypeScript definitions

### Components (`frontend/src/components/`)
UI components
- [ ] `frontend/src/components/ReceiptUploader.tsx` - File upload component
- [ ] `frontend/src/components/ReceiptViewer.tsx` - Receipt display component
- [ ] `frontend/src/components/ItemTable.tsx` - TanStack Table for items
- [ ] `frontend/src/components/FinancialSummary.tsx` - Financial breakdown (Rule 3)
- [ ] `frontend/src/components/Header.tsx` - App header/navigation
- [ ] `frontend/src/components/Footer.tsx` - App footer

### Pages (`frontend/src/pages/`)
Full page views
- [ ] `frontend/src/pages/UploadPage.tsx` - Receipt upload page
- [ ] `frontend/src/pages/DashboardPage.tsx` - User dashboard
- [ ] `frontend/src/pages/ReceiptDetailPage.tsx` - Individual receipt view
- [ ] `frontend/src/pages/SettingsPage.tsx` - User settings

### Services (`frontend/src/services/`)
API communication (Rule 6: Frontend -> Services -> API)
- [ ] `frontend/src/services/api.ts` - Axios instance config
- [ ] `frontend/src/services/receiptService.ts` - Receipt API calls
- [ ] `frontend/src/services/itemService.ts` - Item API calls
- [ ] `frontend/src/services/userService.ts` - User API calls

### Hooks (`frontend/src/hooks/`)
Custom React hooks
- [ ] `frontend/src/hooks/useReceipts.ts` - Receipt query/mutation hook
- [ ] `frontend/src/hooks/useItems.ts` - Item query hook
- [ ] `frontend/src/hooks/useAuth.ts` - Authentication hook

### Types (`frontend/src/types/`)
TypeScript type definitions
- [ ] `frontend/src/types/receipt.ts` - Receipt types matching backend models
- [ ] `frontend/src/types/item.ts` - Item types
- [ ] `frontend/src/types/store.ts` - Store types
- [ ] `frontend/src/types/user.ts` - User types
- [ ] `frontend/src/types/api.ts` - API response/request types

### Assets (`frontend/src/assets/`)
- [ ] `frontend/src/assets/logo.svg` - App logo (if needed)
- [ ] `frontend/src/assets/icons/` - Icon assets

---

## Infrastructure & Config

### Docker
- [ ] `infrastructure/Dockerfile` - Backend container image
- [ ] `infrastructure/.dockerignore` - Docker build exclusions
- [ ] `.dockerignore` - Root level Docker exclusions

### Configuration
- [ ] `.gitignore` - Git ignore rules
- [DONE] `.env` - Exists with secrets
- [DONE] `.env.example` - Created
- [DONE] `backend/.env.example` - Created
- [ ] `frontend/.env.example` - To be created if needed

### Documentation
- [DONE] `docs/BACKEND_SETUP.md` - Created
- [ ] `docs/FRONTEND_SETUP.md` - To be created
- [ ] `docs/API_DOCUMENTATION.md` - OpenAPI docs reference
- [ ] `docs/DATABASE_SCHEMA.md` - MongoDB collections schema
- [ ] `docs/ARCHITECTURE.md` - Architecture overview
- [ ] `docs/DEVELOPMENT_RULES.md` - Reference the 7 rules
- [ ] `README.md` - Project overview

---

## Priority Tiers

### Tier 1: Critical (Start here)
Must exist for basic functionality
- Backend main application files (config, __init__)
- Models (Pydantic schemas with typing)
- API routes
- Services layer
- Database repositories
- ETL pipeline structure

### Tier 2: Important (Next)
Needed for store-specific handling
- Store parsers (at least one - Walmart)
- Normalizer
- Frontend basic pages and components

### Tier 3: Complete (Later)
Polish and edge cases
- ML models
- All store parsers
- Advanced components
- Comprehensive tests

---

## Checklist Commands

To quickly check what's missing:
```bash
# List all missing files
find ./backend -type f -name '*.py' | wc -l  # Should be much higher

# Check for parser files
ls -la ./backend/parsers/*/parser.py

# Check frontend
ls -la ./frontend/src/components/
ls -la ./frontend/src/pages/
```

---

## Notes
- All Python files must have __init__.py in their parent directory (Rule 5: Pydantic everywhere)
- Every service function must use typed parameters and return types
- No dict objects passed between services (Rule 5)
- Financial fields must remain separate across all layers (Rule 3)
- Store parsers must be completely isolated - no shared parsing logic (Rule 1)
- Never use emojis in code or documentation
