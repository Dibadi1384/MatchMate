//
//  MatchProfileView.swift
//  MatchMate
//

import SwiftUI

struct MatchProfileView: View {
    let matchId: String
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    private var match: Match? {
        appState.match(byId: matchId)
    }

    var body: some View {
        ScrollView {
            if let match = match {
                VStack(alignment: .leading, spacing: 20) {
                    HStack(spacing: 16) {
                        if let data = match.profile?.photoData, let img = UIImage(data: data) {
                            Image(uiImage: img)
                                .resizable()
                                .scaledToFill()
                                .frame(width: 80, height: 80)
                                .clipShape(Circle())
                        } else {
                            Image(systemName: "person.circle.fill")
                                .font(.system(size: 80))
                                .foregroundColor(.gray)
                        }
                        VStack(alignment: .leading, spacing: 4) {
                            Text(match.user.email)
                                .font(.title2)
                                .fontWeight(.semibold)
                            Text("Compatibility: \(match.compatibilityScore)%")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            if let p = match.profile, let pronouns = p.pronouns {
                                Text(pronouns)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    .padding(.bottom, 8)

                    if let bio = match.profile?.bio, !bio.isEmpty {
                        Text("Bio")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(bio)
                            .font(.body)
                    }

                    if let age = match.profile?.age {
                        Text("Age: \(age)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    Button(action: startChatting) {
                        Label("Start chatting", systemImage: "bubble.left.and.bubble.right.fill")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.accentColor)
                            .foregroundColor(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                    .padding(.top, 16)
                }
                .padding(24)
            } else {
                ContentUnavailableView("Match not found", systemImage: "person.slash")
            }
        }
        .navigationTitle("Match")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func startChatting() {
        guard let match = match, let me = appState.currentUser else { return }
        let other = match.user
        if let existing = appState.chats.first(where: { $0.participantIds.contains(other.id) }) {
            path.append(HomeDestination.chatDetail(chatId: existing.id))
        } else {
            appState.addChat(with: other)
            if let newChat = appState.chats.last {
                path.append(HomeDestination.chatDetail(chatId: newChat.id))
            }
        }
    }
}

#Preview {
    NavigationStack {
        MatchProfileView(matchId: "m1", path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
