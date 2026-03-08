# MatchMate Frontend Development Plan

This plan follows the user flow chart: **Welcome → Auth (Sign-up / Login) → Home → Profile, Chats, Search for mates**, with all sub-flows and back navigation. It does **not** include implementation; it is a planning document only.

---

## 1. Current State

- **Stack:** SwiftUI (iOS), entry point `MatchMateApp.swift`, main shell `ContentView.swift`.
- **Existing UI:** Welcome-style screen (logo, “MatchMate”, “Behavior-Based Social Matching”) — can become or feed into the **Welcome Page**.
- **Backend:** SQLite schema with `users`, Chrome/YouTube/Calendar/Maps data, `user_compact_profile`, `user_gemini_profile`. No auth, profile (picture/bio/age/pronouns), chats, or matches in schema yet — backend/API work will be needed in parallel or before some phases.

---

## 2. Flowchart Mapping (Screens & Navigation)

| Flowchart node | Screen / component | Notes |
|----------------|--------------------|--------|
| Welcome Page | `WelcomeView` | Sign-up + Login buttons; reuse current ContentView look or refactor into this. |
| Sign-up | `SignUpView` | Email + create password. |
| Profile Creation (post sign-up) | `ProfileCreationView` | Profile picture, bio, age, pronouns. |
| Data upload (dev only) | `DataUploadView` (dev) | Optional; behind dev flag / debug menu. |
| Login | `LoginView` | Email + password. |
| Home Page | `HomeView` | Hub: Profile, Chats, Search for mates. |
| Profile page (edit) | `ProfileView` | View + edit personal info; back → Home. |
| Scrollable chat log | `ChatListView` | List of conversations; back → Home. |
| Scrollable log of chat requests | `ChatRequestsView` | Incoming/outgoing requests; back → Chat list. |
| Individual chat | `ChatDetailView` | One-on-one conversation; back → Requests or Chat list. |
| Search page | `SearchView` | Entry: Business vs Personal relationship. |
| Search (Business) | Same `SearchView` + mode | Dynamic results, professional-life compatibility. |
| Search (Personal) | Same `SearchView` + mode | Dynamic results, personal-life compatibility. |
| Scrollable list of matches | `MatchListView` | Results list; back → Search. |
| Potential compatible match profile | `MatchProfileView` | One match’s profile; back → Match list; “Start chatting”. |
| Start chatting | `ChatDetailView` (new thread) | From match; back → Match profile; long path back to Home. |

---

## 3. Suggested Implementation Phases

### Phase 1: Shell, auth, and home (critical path)

1. **Navigation architecture**
   - Choose pattern: e.g. `NavigationStack` + path, or a small coordinator/router, so every “Back” in the flowchart is explicit.
   - Root: unauthenticated vs authenticated. Unauthenticated root shows Welcome; after login/sign-up (+ optional profile creation + dev data upload) switch to authenticated root (Home).

2. **Welcome Page**
   - Dedicated `WelcomeView`: Sign-up button → Sign-up flow; Login button → Login flow.
   - Option: refactor current `ContentView` into `WelcomeView` and keep `ContentView` as root that chooses between `WelcomeView` and main app (Home-based) by auth state.

3. **Sign-up flow**
   - `SignUpView`: email, password, confirm password; submit → API (to be added); on success → `ProfileCreationView`.
   - `ProfileCreationView`: profile picture (picker), bio, age, pronouns; submit → persist profile; then → dev `DataUploadView` if enabled, else → Home.
   - `DataUploadView`: dev-only; after “upload”/done → Home.

4. **Login flow**
   - `LoginView`: email, password; submit → API; on success → Home.

5. **Home Page**
   - `HomeView`: three entry points — Profile, Chats, Search for mates — each pushing or presenting the corresponding flow. Back from each returns to Home.

**Deliverable:** User can land on Welcome, sign up (email, password, profile creation, optional dev upload) or log in, and reach Home with three clear actions.

---

### Phase 2: Profile

1. **Profile page**
   - `ProfileView`: display and edit personal info (picture, bio, age, pronouns, plus any fields from `user_gemini_profile` you choose to expose).
   - Save/cancel; Back → Home.
   - Ensure same profile model/source used after sign-up profile creation for consistency.

**Deliverable:** From Home → Profile, user can view and edit profile and return to Home.

---

### Phase 3: Search and matches

1. **Search page**
   - `SearchView`: choice “Business relationship” vs “Personal relationship” (e.g. segmented control or two buttons); optional search/filter UI.
   - Depending on choice, call search API (or stub) with mode (business/personal); show loading then results.

2. **Match list**
   - `MatchListView`: scrollable list of matches (dynamic search results); each row navigates to that match’s profile.
   - Back → Search.

3. **Match profile**
   - `MatchProfileView`: show one potential match’s profile (compatibility-focused); “Start chatting” button.
   - Start chatting → create or open thread, navigate to `ChatDetailView`.
   - Back → Match list.

**Deliverable:** Home → Search → choose Business/Personal → see match list → open match profile → start chat → Chat UI (Phase 4).

---

### Phase 4: Chats and requests

1. **Chat list**
   - `ChatListView`: scrollable list of conversations; tap → `ChatDetailView` for that thread.
   - Entry to “chat requests”: e.g. button or section → `ChatRequestsView`.
   - Back → Home.

2. **Chat requests**
   - `ChatRequestsView`: scrollable list of incoming/outgoing chat requests; accept/decline or open request; from here user can open “Individual chat” (e.g. after accept).
   - Back → Chat list.

3. **Individual chat**
   - `ChatDetailView`: used both from Chat list and from “Start chatting” on match profile; show messages, input, send.
   - Back → either Chat list or Match profile depending on entry (can use navigation stack state or a simple “source” enum).

**Deliverable:** Home → Chats → chat log and chat requests; open any conversation; from Search → match → Start chatting, land in same `ChatDetailView` and can navigate back as in flowchart.

---

### Phase 5: Polish and flow alignment

1. **Back arrows**
   - Audit every screen against the flowchart and ensure every “Back” goes to the correct prior screen (Chat list vs Requests vs Match profile vs Search vs Home).

2. **Loading and errors**
   - Loading states for auth, profile save, search, chat load/send; error messages and retry where appropriate.

3. **Data upload (dev)**
   - If not done in Phase 1: ensure Data upload is only reachable after profile creation and only in dev builds; from there flow continues to Home.

4. **Accessibility and layout**
   - Scrollable lists, safe areas, dynamic type if needed; ensure “Scrollable” areas in the flowchart are actually scrollable on small devices.

---

## 4. Technical Notes

- **Auth state:** Single source of truth (e.g. `@Observable` / `ObservableObject` or env object) for “is logged in” and current user; root view switches Welcome vs Home based on this.
- **API surface (to be implemented):** Auth (register, login), profile (create, get, update), search (business/personal, params TBD), matches list, chat requests (list, accept/decline), chats (list, get thread, send message). Schema may need: auth credentials, profile fields (picture URL or blob, bio, age, pronouns), relationships/matches, chat threads, chat messages, chat requests.
- **Navigation:** Prefer one `NavigationStack` (or stack per tab if you add tabs later) and a clear path model so “Back” behavior matches the flowchart exactly and deep links are easier later.
- **Reuse:** `ChatDetailView` is used from Chat list and from Match profile; differentiate by navigation context (e.g. stack path or a “fromMatch” flag) so Back goes to the right place.

---

## 5. Summary Checklist (by flowchart)

- [ ] Welcome Page → Sign-up / Login
- [ ] Sign-up → email + password → Profile Creation → (Data upload dev) → Home
- [ ] Login → email + password → Home
- [ ] Home → Profile, Chats, Search for mates
- [ ] Profile → edit personal info, Back → Home
- [ ] Chats → scrollable chat log → Chat requests and Individual chat, Back paths correct
- [ ] Search → Business / Personal → scrollable match list → Match profile → Start chatting, Back paths correct
- [ ] Start chatting → Individual chat, Back to Match profile; from chat, way back to Home (e.g. via Chat list)

This plan is ready for implementation in the order above (or with Phase 2 and 3 swapped if you want Profile after Search). Do not proceed with implementation until you explicitly request it.
