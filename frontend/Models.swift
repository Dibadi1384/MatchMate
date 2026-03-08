//
//  Models.swift
//  MatchMate
//

import SwiftUI

struct User: Identifiable, Hashable {
    let id: String
    var email: String
}

struct UserProfile: Identifiable {
    var id: String { userId }
    var userId: String
    var photoData: Data?
    var bio: String
    var age: Int?
    var pronouns: String?
}

struct Match: Identifiable {
    let id: String
    let user: User
    let profile: UserProfile?
    let compatibilityScore: Int
    let searchMode: SearchMode
}

enum SearchMode: String, CaseIterable, Hashable {
    case business = "Business relationship"
    case personal = "Personal relationship"
}

struct Chat: Identifiable {
    let id: String
    let participantIds: [String]
    let createdAt: Date
}

struct ChatRequest: Identifiable {
    let id: String
    let fromUserId: String
    let toUserId: String
    let status: ChatRequestStatus
    let createdAt: Date
}

enum ChatRequestStatus: String {
    case pending
    case accepted
    case declined
}

struct Message: Identifiable {
    let id: String
    let senderId: String
    let text: String
    let at: Date
}
