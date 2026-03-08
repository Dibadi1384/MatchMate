//
//  ChatRequestsView.swift
//  MatchMate
//

import SwiftUI

struct ChatRequestsView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    private var requests: [ChatRequest] {
        appState.chatRequests
    }

    var body: some View {
        Group {
            if requests.isEmpty {
                ContentUnavailableView(
                    "No chat requests",
                    systemImage: "envelope.open",
                    description: Text("When someone wants to chat, requests will appear here.")
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(requests) { req in
                            ChatRequestRow(request: req, appState: appState) {
                                path.append(HomeDestination.chatDetail(chatId: req.id))
                            }
                        }
                    }
                    .padding(24)
                }
            }
        }
        .navigationTitle("Chat requests")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ChatRequestRow: View {
    let request: ChatRequest
    @ObservedObject var appState: AppState
    let onAccept: () -> Void

    private var fromUser: User? {
        appState.users.first { $0.id == request.fromUserId }
    }

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "person.circle.fill")
                .font(.system(size: 44))
                .foregroundColor(.gray)

            VStack(alignment: .leading, spacing: 4) {
                Text(fromUser?.email ?? "Unknown")
                    .font(.headline)
                Text(request.status.rawValue)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            if request.status == .pending {
                Button("Accept", action: onAccept)
                    .font(.subheadline)
                    .foregroundColor(.accentColor)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    NavigationStack {
        ChatRequestsView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
