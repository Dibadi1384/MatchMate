//
//  MatchListView.swift
//  MatchMate
//

import SwiftUI

struct MatchListView: View {
    let mode: SearchMode
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    private var matches: [Match] {
        appState.mockMatches(mode: mode)
    }

    var body: some View {
        Group {
            if matches.isEmpty {
                ContentUnavailableView(
                    "No matches yet",
                    systemImage: "person.2.slash",
                    description: Text("Try again later or adjust your preferences.")
                )
            } else {
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(matches) { match in
                            Button(action: { path.append(HomeDestination.matchProfile(matchId: match.id)) }) {
                                HStack(spacing: 16) {
                                    profileThumb(profile: match.profile)
                                    VStack(alignment: .leading, spacing: 4) {
                                        Text(match.user.email)
                                            .font(.headline)
                                            .foregroundColor(.primary)
                                        Text("Compatibility: \(match.compatibilityScore)%")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    Image(systemName: "chevron.right")
                                        .foregroundColor(.secondary)
                                }
                                .padding()
                                .background(Color(.systemBackground))
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.vertical, 8)
                }
            }
        }
        .navigationTitle(mode.rawValue)
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private func profileThumb(profile: UserProfile?) -> some View {
        if let data = profile?.photoData, let img = UIImage(data: data) {
            Image(uiImage: img)
                .resizable()
                .scaledToFill()
                .frame(width: 56, height: 56)
                .clipShape(Circle())
        } else {
            Image(systemName: "person.circle.fill")
                .font(.system(size: 56))
                .foregroundColor(.gray)
        }
    }
}

#Preview {
    NavigationStack {
        MatchListView(mode: .business, path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
