//
//  AppState.swift
//  MatchMate
//

import SwiftUI

// MARK: - Auth flow step (for navigation path)

enum AuthStep: Hashable {
    case signUp
    case login
    case profileCreation
    case dataUpload
}

// MARK: - App state (auth, current user, mock data)

final class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentUser: User?
    @Published var currentUserProfile: UserProfile?

    // Sign-up flow: pass data between steps
    @Published var pendingSignUpEmail: String = ""
    @Published var pendingSignUpPassword: String = ""
    @Published var pendingProfile: UserProfile?

    // In-memory store (replace with API later)
    @Published var users: [User] = []
    @Published var profiles: [UserProfile] = []
    @Published var chats: [Chat] = []
    @Published var chatRequests: [ChatRequest] = []
    @Published var messages: [String: [Message]] = [:] // chatId -> messages

    init() {
        seedMockUsersIfNeeded()
    }

    private func seedMockUsersIfNeeded() {
        guard users.isEmpty else { return }
        let mockUsers = [
            User(id: "mock1", email: "alex@example.com"),
            User(id: "mock2", email: "sam@example.com"),
        ]
        users = mockUsers
        profiles = mockUsers.map { UserProfile(userId: $0.id, bio: "Demo user", age: 28, pronouns: "they/them") }
    }

    /// Call after sign-up form: stores email/password and navigates to profile creation
    func setPendingSignUp(email: String, password: String) {
        pendingSignUpEmail = email
        pendingSignUpPassword = password
    }

    /// Call after profile creation: optionally go to data upload (dev) or finish
    func setPendingProfile(_ profile: UserProfile) {
        pendingProfile = profile
    }

    /// Finish sign-up: create user + profile, log in
    func finishSignUp() {
        let user = User(id: UUID().uuidString, email: pendingSignUpEmail)
        var profile = pendingProfile ?? UserProfile(userId: user.id, bio: "", age: nil, pronouns: nil)
        profile.userId = user.id

        users.append(user)
        profiles.append(profile)
        currentUser = user
        currentUserProfile = profile
        isLoggedIn = true

        pendingSignUpEmail = ""
        pendingSignUpPassword = ""
        pendingProfile = nil
    }

    /// Login (mock: any user in list or create one)
    func login(email: String, password: String) {
        if let user = users.first(where: { $0.email == email }) {
            currentUser = user
            currentUserProfile = profiles.first(where: { $0.userId == user.id })
        } else {
            let user = User(id: UUID().uuidString, email: email)
            let profile = UserProfile(userId: user.id, bio: "", age: nil, pronouns: nil)
            users.append(user)
            profiles.append(profile)
            currentUser = user
            currentUserProfile = profile
        }
        isLoggedIn = true
    }

    func logout() {
        isLoggedIn = false
        currentUser = nil
        currentUserProfile = nil
    }

    func updateProfile(_ profile: UserProfile) {
        if let idx = profiles.firstIndex(where: { $0.userId == profile.userId }) {
            profiles[idx] = profile
        } else {
            profiles.append(profile)
        }
        if profile.userId == currentUser?.id {
            currentUserProfile = profile
        }
    }

    /// Add a chat (e.g. from "Start chatting" with a match)
    func addChat(with otherUser: User) {
        let chat = Chat(
            id: UUID().uuidString,
            participantIds: [currentUser!.id, otherUser.id],
            createdAt: Date()
        )
        chats.append(chat)
        if messages[chat.id] == nil {
            messages[chat.id] = []
        }
    }

    func sendMessage(chatId: String, text: String) {
        let msg = Message(id: UUID().uuidString, senderId: currentUser!.id, text: text, at: Date())
        var list = messages[chatId] ?? []
        list.append(msg)
        messages[chatId] = list
    }

    /// Mock matches for search (Business / Personal)
    func mockMatches(mode: SearchMode) -> [Match] {
        let others = users.filter { $0.id != currentUser?.id }
        return others.prefix(5).enumerated().map { i, u in
            let p = profiles.first(where: { $0.userId == u.id })
            return Match(
                id: "\(mode.rawValue)-\(u.id)",
                user: u,
                profile: p,
                compatibilityScore: 70 + (i % 20),
                searchMode: mode
            )
        }
    }

    /// Find match by id (from either search mode)
    func match(byId id: String) -> Match? {
        for mode in SearchMode.allCases {
            if let m = mockMatches(mode: mode).first(where: { $0.id == id }) {
                return m
            }
        }
        return nil
    }
}
