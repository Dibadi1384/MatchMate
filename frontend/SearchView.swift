//
//  SearchView.swift
//  MatchMate
//

import SwiftUI

struct SearchView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Search for relationship you're looking for")
                .font(.headline)
                .padding(.horizontal)

            Text("Choose search type for dynamic results and compatibility.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .padding(.horizontal)

            VStack(spacing: 12) {
                Button(action: { path.append(HomeDestination.matchList(.business)) }) {
                    HStack {
                        Image(systemName: "briefcase.fill")
                        Text("Business relationship")
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .buttonStyle(.plain)

                Button(action: { path.append(HomeDestination.matchList(.personal)) }) {
                    HStack {
                        Image(systemName: "heart.fill")
                        Text("Personal relationship")
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .padding()
                    .background(Color(.systemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 24)
            .padding(.top, 8)

            Spacer()
        }
        .padding(.top, 20)
        .navigationTitle("Search")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack {
        SearchView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
