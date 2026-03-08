//
//  ChatListView.swift
//  MatchMate
//

import SwiftUI

struct ChatListView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    private var chats: [Chat] {
        appState.chats
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Button(action: { path.append(HomeDestination.chatRequests) }) {
                HStack {
                    Image(systemName: "envelope.badge.fill")
                    Text("Chat requests")
                    Spacer()
                    Image(systemName: "chevron.right")
                }
                .padding()
                .background(Color(.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .buttonStyle(.plain)
            .padding(.horizontal, 24)

            Text("Conversations")
                .font(.headline)
                .padding(.horizontal, 24)

            if chats.isEmpty {
                Spacer()
                ContentUnavailableView(
                    "No conversations yet",
                    systemImage: "bubble.left.and.bubble.right",
                    description: Text("Search for mates and start chatting to see conversations here.")
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(chats) { chat in
                            Button(action: { path.append(HomeDestination.chatDetail(chatId: chat.id)) }) {
                                ChatRowView(chat: chat, appState: appState)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.vertical, 8)
                }
            }
        }
        .padding(.top, 16)
        .navigationTitle("Chats")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ChatRowView: View {
    let chat: Chat
    @ObservedObject var appState: AppState

    private var otherUserId: String? {
        chat.participantIds.first { $0 != appState.currentUser?.id }
    }

    private var otherUser: User? {
        guard let id = otherUserId else { return nil }
        return appState.users.first { $0.id == id }
    }

    private var lastMessage: Message? {
        appState.messages[chat.id]?.last
    }

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "person.circle.fill")
                .font(.system(size: 44))
                .foregroundColor(.gray)

            VStack(alignment: .leading, spacing: 4) {
                Text(otherUser?.email ?? "Unknown")
                    .font(.headline)
                    .foregroundColor(.primary)
                if let msg = lastMessage {
                    Text(msg.text)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    NavigationStack {
        ChatListView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
