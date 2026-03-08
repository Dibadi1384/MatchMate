//
//  HomeView.swift
//  MatchMate
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            ZStack {
                Color("AppCream")
                    .ignoresSafeArea()

                VStack(spacing: 24) {
                    Text("MatchMate")
                        .font(.title)
                        .fontWeight(.bold)
                        .padding(.top, 20)

                    if let email = appState.currentUser?.email {
                        Text("Signed in as \(email)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    VStack(spacing: 16) {
                        NavigationLink(value: HomeDestination.profile) {
                            HomeRow(title: "Profile", icon: "person.circle.fill", subtitle: "Edit personal information")
                        }

                        NavigationLink(value: HomeDestination.chats) {
                            HomeRow(title: "Chats", icon: "bubble.left.and.bubble.right.fill", subtitle: "View conversations and requests")
                        }

                        NavigationLink(value: HomeDestination.search) {
                            HomeRow(title: "Search for mates", icon: "person.2.fill", subtitle: "Business or personal relationships")
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 20)

                    Spacer()

                    Button(action: { appState.logout() }) {
                        Text("Log out")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.bottom, 24)
                }
            }
            .navigationDestination(for: HomeDestination.self) { dest in
                switch dest {
                case .profile:
                    ProfileView()
                case .chats:
                    ChatListView(path: $path)
                case .search:
                    SearchView(path: $path)
                case .matchList(let mode):
                    MatchListView(mode: mode, path: $path)
                case .matchProfile(let matchId):
                    MatchProfileView(matchId: matchId, path: $path)
                case .chatRequests:
                    ChatRequestsView(path: $path)
                case .chatDetail(let chatId):
                    ChatDetailView(chatId: chatId, path: $path)
                }
            }
        }
    }
}

enum HomeDestination: Hashable {
    case profile
    case chats
    case search
    case matchList(SearchMode)
    case matchProfile(matchId: String)
    case chatRequests
    case chatDetail(chatId: String)
}

struct HomeRow: View {
    let title: String
    let icon: String
    let subtitle: String

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.accentColor)
                .frame(width: 44, height: 44)
                .background(Color.accentColor.opacity(0.15))
                .clipShape(RoundedRectangle(cornerRadius: 10))

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    HomeView()
        .environmentObject({
            let a = AppState()
            a.isLoggedIn = true
            a.currentUser = User(id: "1", email: "user@example.com")
            a.currentUserProfile = UserProfile(userId: "1", bio: "Hi", age: 25, pronouns: "she/her")
            return a
        }())
}
