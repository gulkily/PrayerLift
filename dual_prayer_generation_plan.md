# Dual Prayer Generation Development Plan

## Overview
Implement a system that generates both personal and community prayer versions, allowing users to choose which version to share publicly while maintaining access to both perspectives.

## Problem Statement
- Personal prayers written in 3rd person feel awkward when read by the author
- Community prayers written in 1st person feel awkward when read by others
- Users need both perspectives for optimal prayer experience

## Solution: Dual Generation with User Choice

### Phase 1: Backend Infrastructure (2-3 hours)

#### 1.1 Database Schema Updates
- **File**: `main.py` (database models)
- **Changes**: 
  - Add `personal_prayer` field to prayers table
  - Add `selected_version` field (`'personal'` or `'community'`)
  - Update Prayer model class

#### 1.2 AI Service Enhancement  
- **File**: `ai_service.py`
- **Changes**:
  - Modify `generate_prayer_response()` to return both versions
  - Create `generate_personal_prayer()` method
  - Create `generate_community_prayer()` method (current logic)
  - Update method signature to return dict with both prayers

#### 1.3 Prayer Prompt Templates
- **Files**: Create `personal_prayer_prompt.txt`
- **Content**: First-person perspective prompt template
- **Existing**: Keep `prayer_prompt.txt` for community prayers

### Phase 2: API Endpoints (1-2 hours)

#### 2.1 Prayer Submission Endpoint
- **File**: `main.py`
- **Changes**:
  - Update `/prayers` POST route
  - Generate both prayer versions on submission
  - Store both versions in database
  - Default to community version for public display

#### 2.2 Prayer Selection Endpoint
- **File**: `main.py`
- **New Route**: `/prayers/{id}/select-version`
- **Function**: Allow author to switch between personal/community version
- **Authentication**: Only prayer author can switch

### Phase 3: Frontend UI/UX (2-3 hours)

#### 3.1 Prayer Display Enhancement
- **File**: `templates/index.html`
- **Changes**:
  - Show version toggle for prayer authors
  - Display selected version to community
  - Add visual indicator of current version

#### 3.2 Version Selection Interface
- **Implementation**: Toggle switch or radio buttons
- **Location**: Within prayer card for authors only
- **Labels**: "Personal Version" / "Community Version"
- **Real-time**: Update display without page reload

#### 3.3 User Experience Flow
1. User submits prayer request
2. System generates both versions automatically
3. Community version shown by default
4. Author sees toggle to switch versions
5. Author can preview both before selecting public version

### Phase 4: Prayer Generation Logic (2 hours)

#### 4.1 Personal Prayer Prompt
```
Template Focus:
- First-person perspective ("Grant me...", "Help me...")
- Direct relationship with Divine
- Personal reflection and introspection
- Individual spiritual journey language
```

#### 4.2 Community Prayer Prompt  
```
Template Focus:
- Third-person perspective ("Grant [Name]...", "Help them...")
- Intercession language
- Community solidarity expressions
- Inclusive group prayer language
```

#### 4.3 Prompt Engineering
- Test both prompts for quality and consistency
- Ensure appropriate tone for each context
- Validate theological appropriateness

### Phase 5: Testing & Refinement (1-2 hours)

#### 5.1 Functional Testing
- Test dual generation reliability
- Verify version switching works correctly
- Confirm proper authentication checks
- Test database storage of both versions

#### 5.2 User Experience Testing
- Test readability of both versions
- Verify UI clarity and ease of use
- Confirm mobile responsiveness
- Test loading performance with dual generation

#### 5.3 Prayer Quality Assessment
- Review generated prayer quality in both formats
- Ensure theological consistency
- Verify emotional resonance for intended audience
- Test with various prayer request types

## Technical Implementation Details

### Database Migration
```sql
ALTER TABLE prayers ADD COLUMN personal_prayer TEXT;
ALTER TABLE prayers ADD COLUMN selected_version VARCHAR(20) DEFAULT 'community';
```

### API Response Format
```json
{
  "id": "prayer_id",
  "community_prayer": "May God grant John peace...",
  "personal_prayer": "May God grant me peace...",
  "selected_version": "community",
  "can_switch_version": true
}
```

### Frontend Toggle Component
- Clean, accessible toggle interface
- Clear labeling of versions
- Preview capability before switching
- Confirmation for public version changes

## Success Criteria
1. Both prayer versions generate successfully
2. Authors can seamlessly switch between versions
3. Community sees appropriate version based on author's choice
4. Prayer quality maintained in both perspectives
5. UI is intuitive and responsive
6. No performance degradation from dual generation

## Future Enhancements
- A/B testing on prayer effectiveness by version
- Analytics on version preference patterns
- Smart recommendations for optimal version selection
- Integration with prayer request categorization

## Estimated Timeline: 8-10 hours total development time

## Risk Mitigation
- Fallback to single generation if dual generation fails
- Graceful degradation for existing prayers
- Clear user messaging about version differences
- Database backup before schema changes